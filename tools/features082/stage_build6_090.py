"""Stage build 6: build 5 scripts/compiles, runtime3 UI, re-exported banner pages."""
import stage_ui_review090 as stage
stage.SOURCE=stage.ROOT/'BetaGwent/build/release090-final5'
stage.OUT=stage.ROOT/'BetaGwent/build/release090-final6'
stage.UI=stage.ROOT/'BetaGwent/build/release090-banner-runtime3'
stage.NATIVE=stage.ROOT/'BetaGwent/build/clipboard090-r6b'
stage.BANNERS=stage.ROOT/'BetaGwent/build/banners090-sdk-fix5'
if __name__=='__main__':stage.main()
