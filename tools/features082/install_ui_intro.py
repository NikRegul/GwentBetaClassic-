from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).parent))
import install_exchange_fix as install
install.BUILD=install.ROOT/'BetaGwent/build/release082-rc3-ready'
install.SOURCE=install.BUILD/'nextgen/package/Mods/modBetaGwent0924'
install.PREVIOUS=install.ROOT/'BetaGwent/build/release082-rc2/nextgen/package/Mods/modBetaGwent0924'
install.PREVIOUS_VERSION='0.8.2-rc2';install.VERSION='0.8.2-rc3'
install.NAMES=['content/blob0.bundle','content/metadata.store','content/precompiled.rsblob','info.json']
install.PRESERVED=['content/soundspc.cache','content/dep.cache']
if __name__=='__main__':install.main()
