***REMOVED*** This file incorporates code from the AutoGen.
***REMOVED*** The original code can be found at:
***REMOVED*** https://github.com/microsoft/autogen/blob/gaia_multiagent_v01_march_1st/autogen/browser_utils.py

import os
import re
import io
import json
import yaml
import time
import uuid
import requests
import mimetypes
import pathlib
import pathvalidate
import diskcache as dc
from urllib.parse import urljoin, urlparse, unquote, parse_qs
from urllib.request import url2pathname
from typing import Any, Dict, List, Optional, Union, Tuple
from .converter import MarkdownConverter, UnsupportedFormatException, FileConversionException

global_config = yaml.safe_load(open("./config/global.yaml", "r"))


class SimpleTextBrowser:
    """(In preview) An extremely simple text-based web browser comparable to Lynx. Suitable for Agentic use."""

    def __init__(
        self,
        start_page: Optional[str] = None,
        viewport_size: Optional[int] = 1024 * 8,
        downloads_folder: Optional[Union[str, None]] = None,
        bing_api_key: Optional[Union[str, None]] = None,
        request_kwargs: Optional[Union[Dict[str, Any], None]] = None,
    ):
        self.start_page: str = start_page if start_page else "about:blank"
        self.viewport_size = viewport_size  ***REMOVED*** Applies only to the standard uri types
        ***REMOVED*** self.downloads_folder = log_path
        self.history: List[Tuple[str, float]] = list()
        self.page_title: Optional[str] = None
        self.viewport_current_page = 0
        self.viewport_pages: List[Tuple[int, int]] = list()
        self.set_address(self.start_page)
        self.bing_api_key = bing_api_key
        if bing_api_key is  None:
            self.bing_api_key = global_config.get("api_keys").get("bing_api_key")
        
        self.request_kwargs = request_kwargs
        self._mdconvert = MarkdownConverter()
        self._page_content: str = ""

        self._find_on_page_query: Union[str, None] = None
        self._find_on_page_last_result: Union[int, None] = None  ***REMOVED*** Location of the last result

        self.bing_cache = None

    @property
    def address(self) -> str:
        """Return the address of the current page."""
        return self.history[-1][0]

    def set_address(self, uri_or_path: str) -> None:
        ***REMOVED*** TODO: Handle anchors
        self.history.append((uri_or_path, time.time()))

        ***REMOVED*** Handle special URIs
        if uri_or_path == "about:blank":
            self._set_page_content("")
        elif uri_or_path.startswith("bing:"):
            self._bing_search(uri_or_path[len("bing:") :].strip())
        else:
            if (
                not uri_or_path.startswith("http:")
                and not uri_or_path.startswith("https:")
                and not uri_or_path.startswith("file:")
            ):
                if len(self.history) > 1:
                    prior_address = self.history[-2][0]
                    uri_or_path = urljoin(prior_address, uri_or_path)
                    ***REMOVED*** Update the address with the fully-qualified path
                    self.history[-1] = (uri_or_path, self.history[-1][1])
            self._fetch_page(uri_or_path)

        self.viewport_current_page = 0
        self.find_on_page_query = None
        self.find_on_page_viewport = None

    @property
    def viewport(self) -> str:
        """Return the content of the current viewport."""
        bounds = self.viewport_pages[self.viewport_current_page]
        return self.page_content[bounds[0] : bounds[1]]

    @property
    def page_content(self) -> str:
        """Return the full contents of the current page."""
        return self._page_content

    def _set_page_content(self, content: str) -> None:
        """Sets the text content of the current page."""
        self._page_content = content
        self._split_pages()
        if self.viewport_current_page >= len(self.viewport_pages):
            self.viewport_current_page = len(self.viewport_pages) - 1

    def page_down(self) -> None:
        self.viewport_current_page = min(self.viewport_current_page + 1, len(self.viewport_pages) - 1)

    def page_up(self) -> None:
        self.viewport_current_page = max(self.viewport_current_page - 1, 0)

    def find_on_page(self, query: str) -> Union[str, None]:
        """Searches for the query from the current viewport forward, looping back to the start if necessary."""

        ***REMOVED*** Did we get here via a previous find_on_page search with the same query?
        ***REMOVED*** If so, map to find_next
        if query == self._find_on_page_query and self.viewport_current_page == self._find_on_page_last_result:
            return self.find_next()

        ***REMOVED*** Ok it's a new search start from the current viewport
        self._find_on_page_query = query
        viewport_match = self._find_next_viewport(query, self.viewport_current_page)
        if viewport_match is None:
            self._find_on_page_last_result = None
            return None
        else:
            self.viewport_current_page = viewport_match
            self._find_on_page_last_result = viewport_match
            return self.viewport

    def find_next(self) -> None:
        """Scroll to the next viewport that matches the query"""

        if self._find_on_page_query is None:
            return None

        starting_viewport = self._find_on_page_last_result
        if starting_viewport is None:
            starting_viewport = 0
        else:
            starting_viewport += 1
            if starting_viewport >= len(self.viewport_pages):
                starting_viewport = 0

        viewport_match = self._find_next_viewport(self._find_on_page_query, starting_viewport)
        if viewport_match is None:
            self._find_on_page_last_result = None
            return None
        else:
            self.viewport_current_page = viewport_match
            self._find_on_page_last_result = viewport_match
            return self.viewport

    def _find_next_viewport(self, query: str, starting_viewport: int) -> Union[int, None]:
        """Search for matches between the starting viewport looping when reaching the end."""

        if query is None:
            return None

        ***REMOVED*** Normalize the query, and convert to a regular expression
        nquery = re.sub(r"\*", "__STAR__", query)
        nquery = " " + (" ".join(re.split(r"\W+", nquery))).strip() + " "
        nquery = nquery.replace(" __STAR__ ", "__STAR__ ")  ***REMOVED*** Merge isolated stars with prior word
        nquery = nquery.replace("__STAR__", ".*").lower()

        if nquery.strip() == "":
            return None

        idxs = list()
        idxs.extend(range(starting_viewport, len(self.viewport_pages)))
        idxs.extend(range(0, starting_viewport))

        for i in idxs:
            bounds = self.viewport_pages[i]
            content = self.page_content[bounds[0] : bounds[1]]

            ***REMOVED*** TODO: Remove markdown links and images
            ncontent = " " + (" ".join(re.split(r"\W+", content))).strip().lower() + " "
            if re.search(nquery, ncontent):
                return i

        return None

    def visit_page(self, path_or_uri: str) -> str:
        """Update the address, visit the page, and return the content of the viewport."""
        self.set_address(path_or_uri)
        return self.viewport

    def _split_pages(self) -> None:
        ***REMOVED*** Do not split search results
        if self.address.startswith("bing:"):
            self.viewport_pages = [(0, len(self._page_content))]
            return

        ***REMOVED*** Handle empty pages
        if len(self._page_content) == 0:
            self.viewport_pages = [(0, 0)]
            return

        ***REMOVED*** Break the viewport into pages
        self.viewport_pages = []
        start_idx = 0
        while start_idx < len(self._page_content):
            end_idx = min(start_idx + self.viewport_size, len(self._page_content))  ***REMOVED*** type: ignore[operator]
            ***REMOVED*** Adjust to end on a space
            while end_idx < len(self._page_content) and self._page_content[end_idx - 1] not in [" ", "\t", "\r", "\n"]:
                end_idx += 1
            self.viewport_pages.append((start_idx, end_idx))
            start_idx = end_idx

    def _bing_api_call(self, query: str) -> Dict[str, Dict[str, List[Dict[str, Union[str, Dict[str, str]]]]]]:
        ***REMOVED*** Check the cache
        if self.bing_cache is not None:
            cached = self.bing_cache.get(query)
            if cached is not None:
                return cached
        ***REMOVED*** Make sure the key was set
        if self.bing_api_key is None:
            raise ValueError("Missing Bing API key.")

        ***REMOVED*** Prepare the request parameters
        request_kwargs = self.request_kwargs.copy() if self.request_kwargs is not None else {}

        if "headers" not in request_kwargs:
            request_kwargs["headers"] = {}
        request_kwargs["headers"]["Ocp-Apim-Subscription-Key"] = self.bing_api_key

        if "params" not in request_kwargs:
            request_kwargs["params"] = {}
        request_kwargs["params"]["q"] = query
        request_kwargs["params"]["textDecorations"] = False
        request_kwargs["params"]["textFormat"] = "raw"

        request_kwargs["stream"] = False
        request_kwargs["timeout"] = (5,10)

        ***REMOVED*** Make the request
        response = None
        for _ in range(2):
            try:
                response = requests.get("https://api.bing.microsoft.com/v7.0/search", **request_kwargs)
                response.raise_for_status()
                break
            except Exception:
                pass
            time.sleep(1)
        if response is None:
            raise requests.exceptions.RequestException("Failed to fetch Bing search results.")
        results = response.json()

        ***REMOVED*** Cache the results
        if self.bing_cache is not None:
            self.bing_cache.set(query, results)

        return results  ***REMOVED*** type: ignore[no-any-return]

    def _bing_search(self, query: str) -> None:
        results = self._bing_api_call(query)

        def _prev_visit(url):
            for i in range(len(self.history) - 1, -1, -1):
                if self.history[i][0] == url:
                    ***REMOVED*** Todo make this more human-friendly
                    return f"You previously visited this page {round(time.time() - self.history[i][1])} seconds ago.\n"
            return ""

        web_snippets: List[str] = list()
        idx = 0
        if "webPages" in results:
            for page in results["webPages"]["value"]:
                idx += 1
                web_snippets.append(
                    f"{idx}. [{page['name']}]({page['url']})\n{_prev_visit(page['url'])}{page['snippet']}"
                )
                if "deepLinks" in page:
                    for dl in page["deepLinks"]:
                        idx += 1
                        web_snippets.append(
                            f"{idx}. [{dl['name']}]({dl['url']})\n{_prev_visit(dl['url'])}{dl['snippet'] if 'snippet' in dl else ''}"
                        )

        news_snippets = list()
        if "news" in results:
            for page in results["news"]["value"]:
                idx += 1
                datePublished = ""
                if "datePublished" in page:
                    datePublished = "\nDate published: " + page["datePublished"].split("T")[0]
                news_snippets.append(
                    f"{idx}. [{page['name']}]({page['url']})\n{_prev_visit(page['url'])}{page['description']}{datePublished}"
                )

        video_snippets = list()
        if "videos" in results:
            for page in results["videos"]["value"]:
                if not page["contentUrl"].startswith("https://www.youtube.com/watch?v="):
                    continue
                idx += 1
                datePublished = ""
                if "datePublished" in page:
                    datePublished = "\nDate published: " + page["datePublished"].split("T")[0]
                video_snippets.append(
                    f"{idx}. [{page['name']}]({page['contentUrl']})\n{_prev_visit(page['contentUrl'])}{page.get('description', '')}{datePublished}"
                )

        self.page_title = f"{query} - Search"

        content = (
            f"A Bing search for '{query}' found {len(web_snippets) + len(news_snippets) + len(video_snippets)} results:\n\n***REMOVED******REMOVED*** Web Results\n"
            + "\n\n".join(web_snippets)
        )
        if len(news_snippets) > 0:
            content += "\n\n***REMOVED******REMOVED*** News Results:\n" + "\n\n".join(news_snippets)
        if len(video_snippets) > 0:
            content += "\n\n***REMOVED******REMOVED*** Video Results:\n" + "\n\n".join(video_snippets)

        self._set_page_content(content)

    def _fetch_page(self, url: str) -> None:
        download_path = ""
        response = None
        print(f'Fetching page: {url}')
        try:
            if url.startswith("file://"):
                download_path = os.path.normcase(os.path.normpath(unquote(url[8:])))
                res = self._mdconvert.convert_local(download_path)
                self.page_title = res.title
                self._set_page_content(res.text_content)
            else:
                ***REMOVED*** Prepare the request parameters
                request_kwargs = self.request_kwargs.copy() if self.request_kwargs is not None else {}
                request_kwargs["stream"] = True
                request_kwargs["timeout"] = (5,10)  

                ***REMOVED*** Send a HTTP request to the URL
                response = requests.get(url, **request_kwargs)
                response.raise_for_status()

                ***REMOVED*** If the HTTP request was successful
                content_type = response.headers.get("content-type", "")

                ***REMOVED*** Text or HTML
                if "text/" in content_type.lower():
                    res = self._mdconvert.convert_response(response)
                    self.page_title = res.title
                    self._set_page_content(res.text_content)
                ***REMOVED*** A download
                else:
                    ***REMOVED*** Try producing a safe filename
                    fname = None
                    download_path = None
                    try:
                        fname = pathvalidate.sanitize_filename(os.path.basename(urlparse(url).path)).strip()
                        download_path = os.path.abspath(os.path.join(self.downloads_folder, fname))

                        suffix = 0
                        while os.path.exists(download_path) and suffix < 1000:
                            suffix += 1
                            base, ext = os.path.splitext(fname)
                            new_fname = f"{base}__{suffix}{ext}"
                            download_path = os.path.abspath(os.path.join(self.downloads_folder, new_fname))

                    except NameError:
                        pass

                    ***REMOVED*** No suitable name, so make one
                    if fname is None:
                        extension = mimetypes.guess_extension(content_type)
                        if extension is None:
                            extension = ".download"
                        fname = str(uuid.uuid4()) + extension
                        download_path = os.path.abspath(os.path.join(self.downloads_folder, fname))

                    ***REMOVED*** Open a file for writing
                    with open(download_path, "wb") as fh:
                        for chunk in response.iter_content(chunk_size=512):
                            fh.write(chunk)

                    ***REMOVED*** Render it
                    local_uri = pathlib.Path(download_path).as_uri()
                    self.set_address(local_uri)

        except UnsupportedFormatException as e:
            print(f'Unsupported format: {e}')
            self.page_title = ("Download complete.",)
            self._set_page_content(f"***REMOVED*** Download complete\n\nSaved file to '{download_path}'")
        except FileConversionException as e:
            print(f'File conversion error: {e}')
            self.page_title = ("Download complete.",)
            self._set_page_content(f"***REMOVED*** Download complete\n\nSaved file to '{download_path}'")
        except FileNotFoundError:
            self.page_title = "Error 404"
            self._set_page_content(f"***REMOVED******REMOVED*** Error 404\n\nFile not found: {download_path}")
        except requests.exceptions.RequestException:
            if response is None:
                self.page_title = "Error"
                self._set_page_content(f"***REMOVED******REMOVED*** Error\n\nFailed to fetch '{url}'")
            else:
                self.page_title = f"Error {response.status_code}"

                ***REMOVED*** If the error was rendered in HTML we might as well render it
                content_type = response.headers.get("content-type", "")
                if content_type is not None and "text/html" in content_type.lower():
                    res = self._mdconvert.convert(response)
                    self.page_title = f"Error {response.status_code}"
                    text_content = getattr(res, "text_content", None)
                    self._set_page_content(f"***REMOVED******REMOVED*** Error {response.status_code}\n\n{text_content}")
                else:
                    text = ""
                    for chunk in response.iter_content(chunk_size=512, decode_unicode=True):
                        if type(chunk) == str:
                            text += chunk
                    self.page_title = f"Error {response.status_code}"
                    self._set_page_content(f"***REMOVED******REMOVED*** Error {response.status_code}\n\n{text}")


***REMOVED*** ***REMOVED***https://stackoverflow.com/questions/10123929/fetch-a-file-from-a-local-url-with-python-requests
***REMOVED*** class LocalFileAdapter(requests.adapters.BaseAdapter):
***REMOVED***     """Protocol Adapter to allow Requests to GET file:// URLs"""
***REMOVED***
***REMOVED***     @staticmethod
***REMOVED***     def _chkpath(method, path):
***REMOVED***         """Return an HTTP status for the given filesystem path."""
***REMOVED***         if method.lower() in ("put", "delete"):
***REMOVED***             return 501, "Not Implemented"
***REMOVED***         elif method.lower() not in ("get", "head"):
***REMOVED***             return 405, "Method Not Allowed"
***REMOVED***         elif not os.path.exists(path):
***REMOVED***             return 404, "File Not Found"
***REMOVED***         elif not os.access(path, os.R_OK):
***REMOVED***             return 403, "Access Denied"
***REMOVED***         else:
***REMOVED***             return 200, "OK"
***REMOVED***
***REMOVED***     def send(self, req, **kwargs):
***REMOVED***         """Return the file specified by the given request"""
***REMOVED***         path = os.path.normcase(os.path.normpath(url2pathname(req.path_url)))
***REMOVED***         response = requests.Response()
***REMOVED***
***REMOVED***         response.status_code, response.reason = self._chkpath(req.method, path)
***REMOVED***         if response.status_code == 200 and req.method.lower() != "head":
***REMOVED***             try:
***REMOVED***                 if os.path.isfile(path):
***REMOVED***                     response.raw = open(path, "rb")
***REMOVED***                 else:  ***REMOVED*** List the directory
***REMOVED***                     response.headers["content-type"] = "text/html"
***REMOVED***                     pardir = os.path.normpath(os.path.join(path, os.pardir))
***REMOVED***                     pardir_uri = pathlib.Path(pardir).as_uri()
***REMOVED***                     listing = f"""
***REMOVED*** <!DOCTYPE html>
***REMOVED*** <html>
***REMOVED***   <head>
***REMOVED***     <title>Index of {html.escape(path)}</title>
***REMOVED***   </head>
***REMOVED***   <body>
***REMOVED***     <h1>Index of {html.escape(path)}</h1>
***REMOVED***
***REMOVED***     <a href="{html.escape(pardir_uri, quote=True)}">.. (parent directory)</a>
***REMOVED***
***REMOVED***     <table>
***REMOVED***     <tr>
***REMOVED***        <th>Name</th><th>Size</th><th>Date modified</th>
***REMOVED***     </tr>
***REMOVED*** """
***REMOVED***
***REMOVED***                     for entry in os.listdir(path):
***REMOVED***                         full_path = os.path.normpath(os.path.join(path, entry))
***REMOVED***                         full_path_uri = pathlib.Path(full_path).as_uri()
***REMOVED***                         size = ""
***REMOVED***
***REMOVED***                        if os.path.isdir(full_path):
***REMOVED***                            entry = entry + os.path.sep
***REMOVED***                        else:
***REMOVED***                            size = str(os.path.getsize(full_path))
***REMOVED***
***REMOVED***                        listing += (
***REMOVED***                            "<tr>\n"
***REMOVED***                            + f'<td><a href="{html.escape(full_path_uri, quote=True)}">{html.escape(entry)}</a></td>'
***REMOVED***                            + f"<td>{html.escape(size)}</td>"
***REMOVED***                            + f"<td>{html.escape(entry)}</td>"
***REMOVED***                            + "</tr>"
***REMOVED***                        )
***REMOVED***
***REMOVED***                    listing += """
***REMOVED***    </table>
***REMOVED***  </body>
***REMOVED*** </html>
***REMOVED*** """
***REMOVED***
***REMOVED***                    response.raw = io.StringIO(listing)
***REMOVED***            except (OSError, IOError) as err:
***REMOVED***                response.status_code = 500
***REMOVED***                response.reason = str(err)
***REMOVED***
***REMOVED***        if isinstance(req.url, bytes):
***REMOVED***            response.url = req.url.decode("utf-8")
***REMOVED***        else:
***REMOVED***            response.url = req.url
***REMOVED***
***REMOVED***        response.request = req
***REMOVED***        response.connection = self
***REMOVED***
***REMOVED***        return response
***REMOVED***
***REMOVED***    def close(self):
***REMOVED***        pass
