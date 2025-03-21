def serverClassFactory(serverIface):
    from .main import ClinePrinterServer

    return ClinePrinterServer(serverIface)
