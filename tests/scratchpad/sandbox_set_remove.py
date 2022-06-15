from py4cytoscape import *

BASE_URL = "http://192.168.4.189:1234/v1"
BASE_URL = DEFAULT_BASE_URL

sandbox_set('mybox', copy_samples=False, reinitialize=True, base_url=BASE_URL)
sandbox_remove('mybox', base_url=BASE_URL)
sandbox_set('mybox', copy_samples=False, reinitialize=True, base_url=BASE_URL)
sandbox_remove('mybox', base_url=BASE_URL)
sandbox_set('mybox', copy_samples=False, reinitialize=True, base_url=BASE_URL)
sandbox_remove('mybox', base_url=BASE_URL)
sandbox_set('mybox', copy_samples=False, reinitialize=True, base_url=BASE_URL)
sandbox_remove('mybox', base_url=BASE_URL)
sandbox_set('mybox', copy_samples=False, reinitialize=True, base_url=BASE_URL)
sandbox_remove('mybox', base_url=BASE_URL)