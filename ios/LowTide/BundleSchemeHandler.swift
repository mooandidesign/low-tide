import Foundation
import WebKit

/// Serves `dist/` from the app bundle at `lowtide://localhost/…`.
///
/// `WKWebView.loadFileURL` gives each file a unique origin, so the game's
/// ES module imports (`rpg.mjs` and the files it imports) fail. A custom
/// scheme keeps one origin, which is also what localStorage is stored under.
/// The website data store must stay the persistent default store.
final class BundleSchemeHandler: NSObject, WKURLSchemeHandler {
    static let scheme = "lowtide"
    static let origin = "lowtide://localhost"

    private let root: URL
    private let lock = NSLock()
    private var stopped = Set<ObjectIdentifier>()

    override init() {
        let resources = Bundle.main.resourceURL ?? URL(fileURLWithPath: "/")
        root = resources.appendingPathComponent("dist", isDirectory: true)
        super.init()
    }

    func webView(_ webView: WKWebView, start urlSchemeTask: WKURLSchemeTask) {
        let method = (urlSchemeTask.request.httpMethod ?? "GET").uppercased()
        if method == "OPTIONS" {
            respond(urlSchemeTask, status: 204, mime: "text/plain", body: Data())
            return
        }
        guard method == "GET" || method == "HEAD" else {
            respond(urlSchemeTask, status: 405, mime: "text/plain; charset=utf-8", body: Data("Method not allowed".utf8))
            return
        }
        guard let url = urlSchemeTask.request.url, let fileURL = fileURL(for: url) else {
            respond(urlSchemeTask, status: 404, mime: "text/plain; charset=utf-8", body: Data("Not found".utf8))
            return
        }
        do {
            let data = try Data(contentsOf: fileURL)
            let body = method == "HEAD" ? Data() : data
            respond(urlSchemeTask, status: 200, mime: mimeType(for: fileURL), body: body, contentLength: data.count)
        } catch {
            respond(urlSchemeTask, status: 500, mime: "text/plain; charset=utf-8", body: Data("Could not read bundled file".utf8))
        }
    }

    func webView(_ webView: WKWebView, stop urlSchemeTask: WKURLSchemeTask) {
        lock.lock()
        stopped.insert(ObjectIdentifier(urlSchemeTask as AnyObject))
        lock.unlock()
    }

    /// Map a `lowtide://localhost/…` path onto a file inside the bundled `dist` directory.
    private func fileURL(for url: URL) -> URL? {
        let parts = url.path.split(separator: "/").map(String.init)
        guard parts.allSatisfy({ $0 != "." && $0 != ".." }) else { return nil }
        let relative = parts.isEmpty ? "index.html" : parts.joined(separator: "/")
        let candidate = root.appendingPathComponent(relative).standardizedFileURL
        let rootPath = root.standardizedFileURL.path
        let prefix = rootPath.hasSuffix("/") ? rootPath : rootPath + "/"
        guard candidate.path.hasPrefix(prefix) else { return nil }
        var isDirectory: ObjCBool = false
        guard FileManager.default.fileExists(atPath: candidate.path, isDirectory: &isDirectory),
              !isDirectory.boolValue else {
            return nil
        }
        return candidate
    }

    private func mimeType(for fileURL: URL) -> String {
        switch fileURL.pathExtension.lowercased() {
        case "html", "htm":
            return "text/html; charset=utf-8"
        case "css":
            return "text/css; charset=utf-8"
        case "js", "mjs":
            // Module scripts are rejected unless the MIME type is JavaScript.
            return "text/javascript"
        case "webp":
            return "image/webp"
        case "svg":
            return "image/svg+xml"
        case "json":
            return "application/json"
        case "png":
            return "image/png"
        case "jpg", "jpeg":
            return "image/jpeg"
        default:
            return "application/octet-stream"
        }
    }

    private func respond(
        _ task: WKURLSchemeTask,
        status: Int,
        mime: String,
        body: Data,
        contentLength: Int? = nil
    ) {
        lock.lock()
        defer { lock.unlock() }
        if stopped.contains(ObjectIdentifier(task as AnyObject)) { return }
        guard let url = task.request.url else { return }
        let headers = [
            "Content-Type": mime,
            "Content-Length": String(contentLength ?? body.count),
            "Cache-Control": "no-cache",
            "Access-Control-Allow-Origin": "*",
        ]
        guard let response = HTTPURLResponse(url: url, statusCode: status, httpVersion: "HTTP/1.1", headerFields: headers) else {
            return
        }
        task.didReceive(response)
        if !body.isEmpty {
            task.didReceive(body)
        }
        task.didFinish()
    }
}
