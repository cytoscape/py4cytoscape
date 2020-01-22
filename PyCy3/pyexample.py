## @package pyexample
#  Documentation for this module.
#
#  More details.

## For func
# @title Get the list of Cytoscape networks
#
# @description Returns the list of Cytoscape network names in the current Cytoscape session
# @param base.url (optional) Ignore unless you need to specify a custom domain,
# port or version to connect to the CyREST API. Default is http://localhost:1234
# and the latest version of the CyREST API supported by this version of RCy3.
# @return \code{list}
# @author Alexander Pico, Tanja Muetze, Georgi Kolishovski, Paul Shannon
# @examples \dontrun{
# getNetworkList()
# # 3
# }
# @export
def func():
   pass

## Documentation for a class.
#
#  More details.
class PyClass:

    ## The constructor.
    def __init__(self):
        self._memVar = 0;

    ## Documentation for a method.
    #  @param self The object pointer.
    def PyMethod(self):
        pass

    ## A class variable.
    classVar = 0;

    ## @var _memVar
    #  a member variable
