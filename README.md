# netstream
 Parallel asynchronous network requests via tor proxy

 ## Usage
 Simply feed all page urls to the Netstream module[^1] and it will start a parallel asynchronous process to load the required resources

 ## Examples
 ```python
  from netstream import Netstream

  urls = [fr'https://ya.ru', fr'http://jsonip.com']
  ns = Netstream()
  data = ns.run(targets=urls)
  complete = f'{100*ns.received/ns.total:.0f}' if ns.total else 0
  print(f'result {complete}% (errors {ns.total-ns.received}) ')
  print(f'{data}')
   ```
  ## Remarks
  Netstream used Tor Browser resources.
  [^1]: Tor browser must be running and active at this time
