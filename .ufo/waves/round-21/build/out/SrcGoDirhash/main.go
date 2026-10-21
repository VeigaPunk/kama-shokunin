// Scratch probe (kama-r21 SrcGoDirhash): executed behaviour of golang.org/x/mod
// v0.42.0 sumdb/dirhash and zip on symbolic links. Usage: go run . <workdir>
package main

import (
	"archive/zip"
	"bytes"
	"fmt"
	"io/fs"
	"os"
	"path/filepath"

	"golang.org/x/mod/module"
	"golang.org/x/mod/sumdb/dirhash"
	xzip "golang.org/x/mod/zip"
)

const prefix = "example.com/m@v1.0.0"

var work string

func must(err error) {
	if err != nil {
		panic(err)
	}
}

func merge(a, b map[string]string) map[string]string {
	out := map[string]string{}
	for k, v := range a {
		out[k] = v
	}
	for k, v := range b {
		out[k] = v
	}
	return out
}

// tree writes regular files, then symlinks (name -> target), under root.
func tree(root string, files, links map[string]string) string {
	must(os.RemoveAll(root))
	for name, body := range files {
		p := filepath.Join(root, name)
		must(os.MkdirAll(filepath.Dir(p), 0o755))
		must(os.WriteFile(p, []byte(body), 0o644))
	}
	for name, target := range links {
		p := filepath.Join(root, name)
		must(os.MkdirAll(filepath.Dir(p), 0o755))
		must(os.Symlink(target, p))
	}
	return root
}

// hashOf returns the Hash1 directory hash, or an ERR: string on failure.
func hashOf(root string) string {
	h, err := dirhash.HashDir(root, prefix, dirhash.Hash1)
	if err != nil {
		return "ERR:" + err.Error()
	}
	return h
}

func probe(label, root string) {
	files, ferr := dirhash.DirFiles(root, prefix)
	fmt.Printf("%-26s DirFiles err=%v files=%v\n", label, ferr, files)
	fmt.Printf("%-26s HashDir  h=%q\n", label, hashOf(root))
}

type zent struct {
	name string
	body string
	mode fs.FileMode
}

func writeZip(path string, ents []zent) string {
	f, err := os.Create(path)
	must(err)
	zw := zip.NewWriter(f)
	for _, e := range ents {
		hdr := &zip.FileHeader{Name: prefix + "/" + e.name, Method: zip.Store}
		hdr.SetMode(e.mode)
		w, err := zw.CreateHeader(hdr)
		must(err)
		_, err = w.Write([]byte(e.body))
		must(err)
	}
	must(zw.Close())
	must(f.Close())
	return path
}

func listZip(path string) {
	zr, err := zip.OpenReader(path)
	must(err)
	defer zr.Close()
	for _, f := range zr.File {
		fmt.Printf("   entry %-44s mode=%s\n", f.Name, f.Mode())
	}
}

func walkModes(root string) {
	err := filepath.WalkDir(root, func(p string, _ fs.DirEntry, err error) error {
		if err != nil {
			return err
		}
		info, err := os.Lstat(p)
		if err != nil {
			return err
		}
		rel, _ := filepath.Rel(root, p)
		fmt.Printf("   %s %s\n", info.Mode(), rel)
		return nil
	})
	fmt.Printf("   walk err=%v\n", err)
}

func main() {
	work = os.Args[1]
	must(os.MkdirAll(work, 0o755))
	regs := map[string]string{
		"lib/libllama.so.0.0.1": "AAAA\n",
		"lib/libalt.so":         "AAAA\n",
		"lib/libnew.so":         "BBBB\n",
	}
	soname := map[string]string{"lib/libllama.so.0": "libllama.so.0.0.1"}
	sub := map[string]string{"sub/inner.txt": "CCCC\n"}
	mv := module.Version{Path: "example.com/m", Version: "v1.0.0"}

	fmt.Println("== A. directory variant: dirhash.DirFiles / HashDir(Hash1) ==")
	probe("A1 soname link", tree(work+"/a1", regs, soname))
	probe("A2 retarget same bytes", tree(work+"/a2", regs, map[string]string{"lib/libllama.so.0": "libalt.so"}))
	probe("A3 retarget diff bytes", tree(work+"/a3", regs, map[string]string{"lib/libllama.so.0": "libnew.so"}))
	probe("A4 link removed", tree(work+"/a4", regs, nil))
	probe("A5 regular copy same bytes", tree(work+"/a5", merge(regs, map[string]string{"lib/libllama.so.0": "AAAA\n"}), nil))
	probe("A6 dangling link", tree(work+"/a6", regs, merge(soname, map[string]string{"lib/dangling": "nowhere"})))
	probe("A7 link to directory", tree(work+"/a7", merge(regs, sub), map[string]string{"lib/dirlink": "../sub"}))
	must(os.RemoveAll(work + "/a8"))
	must(os.Symlink(work+"/a1", work+"/a8"))
	probe("A8 symlinked root", work+"/a8")

	fmt.Println("== A9. chain shortcut (C2 grid cell link-same-resolution-shortcut analogue) ==")
	chainBefore := tree(work+"/a9", regs, map[string]string{"lib/libllama.so.0": "libllama.so", "lib/libllama.so": "libllama.so.0.0.1"})
	chainAfter := tree(work+"/a9s", regs, map[string]string{"lib/libllama.so.0": "libllama.so.0.0.1", "lib/libllama.so": "libllama.so.0.0.1"})
	hb9, ha9 := hashOf(chainBefore), hashOf(chainAfter)
	fmt.Printf("A9 before=%q after=%q equal=%v\n", hb9, ha9, hb9 == ha9)

	fmt.Println("== D. equality summary (HashDir, Hash1) ==")
	h1 := hashOf(tree(work+"/d1", regs, soname))
	h2 := hashOf(tree(work+"/d2", regs, map[string]string{"lib/libllama.so.0": "libalt.so"}))
	h3 := hashOf(tree(work+"/d3", regs, map[string]string{"lib/libllama.so.0": "libnew.so"}))
	h5 := hashOf(tree(work+"/d5", merge(regs, map[string]string{"lib/libllama.so.0": "AAAA\n"}), nil))
	fmt.Printf("D1 link vs identical-bytes retarget equal=%v\n", h1 == h2)
	fmt.Printf("D2 link vs different-bytes retarget equal=%v\n", h1 == h3)
	fmt.Printf("D3 link vs regular copy of identical bytes equal=%v\n", h1 == h5)

	fmt.Println("== B. module zip variant: xzip.CheckDir / CreateFromDir / HashZip ==")
	b1 := tree(work+"/b1", merge(regs, sub), merge(soname, map[string]string{"lib/dirlink": "../sub", "lib/dangling": "nowhere"}))
	cf, cerr := xzip.CheckDir(b1)
	fmt.Printf("B1 CheckDir err=%v valid=%v\n   omitted=%v\n   invalid=%v\n", cerr, cf.Valid, cf.Omitted, cf.Invalid)
	var buf bytes.Buffer
	cerr2 := xzip.CreateFromDir(&buf, mv, b1)
	fmt.Printf("B2 CreateFromDir err=%v bytes=%d\n", cerr2, buf.Len())
	bz := work + "/b1.zip"
	must(os.WriteFile(bz, buf.Bytes(), 0o644))
	listZip(bz)
	hz, ez := dirhash.HashZip(bz, dirhash.Hash1)
	fmt.Printf("B2 HashZip h=%q err=%v\n", hz, ez)
	breg := tree(work+"/b1reg", merge(regs, sub), nil)
	hd, ed := dirhash.HashDir(breg, prefix, dirhash.Hash1)
	fmt.Printf("B3 HashDir(regular-only) h=%q err=%v equal_HashZip=%v\n", hd, ed, hd == hz)
	hl, el := dirhash.HashDir(b1, prefix, dirhash.Hash1)
	fmt.Printf("B4 HashDir(tree with links) h=%q err=%v\n", hl, el)

	fmt.Println("== C. zip entries with symlink mode: xzip.CheckZip / HashZip / Unzip ==")
	ca := writeZip(work+"/ca.zip", []zent{
		{"lib/libllama.so.0.0.1", "AAAA\n", 0o644},
		{"lib/libllama.so.0", "libllama.so.0.0.1", fs.ModeSymlink | 0o777},
	})
	cb := writeZip(work+"/cb.zip", []zent{
		{"lib/libllama.so.0.0.1", "AAAA\n", 0o644},
		{"lib/libllama.so.0", "libllama.so.0.0.1", 0o644},
	})
	fmt.Println("   symlink-mode zip:")
	listZip(ca)
	fmt.Println("   regular-mode zip:")
	listZip(cb)
	cfa, ea := xzip.CheckZip(mv, ca)
	fmt.Printf("C1 CheckZip(symlink entry) err=%v valid=%v invalid=%v\n", ea, cfa.Valid, cfa.Invalid)
	cfb, eb := xzip.CheckZip(mv, cb)
	fmt.Printf("C1 CheckZip(regular entry) err=%v valid=%v invalid=%v\n", eb, cfb.Valid, cfb.Invalid)
	ha, eha := dirhash.HashZip(ca, dirhash.Hash1)
	hb, ehb := dirhash.HashZip(cb, dirhash.Hash1)
	fmt.Printf("C2 HashZip(symlink entry) h=%q err=%v\n", ha, eha)
	fmt.Printf("C2 HashZip(regular entry) h=%q err=%v equal=%v\n", hb, ehb, ha == hb)
	must(os.RemoveAll(work + "/cu"))
	uerr := xzip.Unzip(work+"/cu", mv, ca)
	fmt.Printf("C3 Unzip(symlink-mode zip) err=%v\n", uerr)
	walkModes(work + "/cu")
}
