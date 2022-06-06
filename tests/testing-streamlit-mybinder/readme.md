[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/HydroGeoSines/HydroGeoSines/tests/testing-streamlit-mybinder/master?urlpath=proxy/8501/)
***
# testing-streamlit-mybinder
A repo tryna see if you could run a streamlit app on mybinder

Inspired by this thread: https://discuss.streamlit.io/t/jupyterhub-streamlit/1238/5

It finally worked when github user [op07n](https://github.com/op07n) forked and fixed `streamlit_call.py`

# Requirements
3 files:
* `requirements.txt` or `evironment.yml` with 
  - nbserverproxy
  - streamlit
  - jupyter-server-proxy
* a jupyter server extension script:
  - Here we called it `streamlit_call.py` and it's fairly simple
  ```python
  from subprocess import Popen

  def load_jupyter_server_extension(nbapp):
      """serve the streamlit app"""
      Popen(["streamlit", "hello", "--browser.serverAddress=0.0.0.0", "--server.enableCORS=False"])
  ```
* `postBuild` which enables nbserverproxy, moves the extension script and enables it
  ```python
    # enable nbserverproxy
    jupyter serverextension enable --sys-prefix nbserverproxy
    # streamlit launches at startup
    mv .binder/streamlit_call.py ${NB_PYTHON_PREFIX}/lib/python*/site-packages/
    # enable streamlit extension
    jupyter serverextension enable --sys-prefix streamlit_call
    ```

To open by default you'd add `?urlpath=proxy/8501/` to the end of your mybinder link.
For example, this repo's link is
https://mybinder.org/v2/gh/chekos/testing-streamlit-mybinder/master?urlpath=proxy/8501/

| WARNING: Make sure you have a trailing `/` at the end (`proxy/8501/` :thumbsup: - `proxy/8501` :thumbsdown:) |
| --- |
