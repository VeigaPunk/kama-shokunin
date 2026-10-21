/* LinksLoaderProof decoy: built with -Wl,-soname,libggml.so.0 so that a symlink
 * retarget to this file keeps the requested soname. It exports one marker symbol,
 * has no dependencies, and implements no ggml ABI. It is not a ggml build. */
int linksloaderproof_decoy_marker(void)
{
    return 42;
}
