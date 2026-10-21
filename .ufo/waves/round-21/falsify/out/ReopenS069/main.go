// Scratch probe (kama-r21 ReopenS069): executed behaviour of golang.org/x/mod
// v0.42.0 sumdb/dirhash and zip on symbolic links. Usage: go run . <workdir>
package main

import (
	"archive/zip"
	"bytes"
	"fmt"
	"io/fs"
	"os"
	"path/filepath"
	"sort"
	"strings"

	"golang.org/x/mod/module"
	"golang.org/x/mod/sumdb/dirhash"
	xzip "golang.org/x/mod/zip"
)

const prefix = "example.com/m@v1.0.0"

var mod = module.Version{Path: "example.com/m", Version: "v1.0.0"}

func must(err error) {
	if err != nil {
		panic(err)
	}
}

func writeFile(root, rel, content string) {
	p := filepath.Join(root, rel)
	must(os.MkdirAll(filepath.Dir(p), 0o755))
	must(os.WriteFile(p, []byte(content), 0o644))
}

func makeLink(root, rel, target string) {
	p := filepath.Join(root, rel)
	must(os.MkdirAll(filepath.Dir(p), 0o755))
	must(os.Symlink(target, p))
}

func h1(dir string) string {
	h, err := dirhash.HashDir(dir, prefix, dirhash.Hash1)
	if err != nil {
		return "ERR(" + err.Error() + ")"
	}
	return h
}

func names(dir string) string {
	files, err := dirhash.DirFiles(dir, prefix)
	if err != nil {
		return "ERR(" + err.Error() + ")"
	}
	sort.Strings(files)
	return strings.Join(files, " ")
}

func mkZip(path string, symlinkMode bool, content string) {
	f, err := os.Create(path)
	must(err)
	zw := zip.NewWriter(f)
	fh := &zip.FileHeader{Name: prefix + "/link.txt", Method: zip.Store}
	if symlinkMode {
		fh.SetMode(fs.ModeSymlink | 0o777)
	} else {
		fh.SetMode(0o644)
	}
	wr, err := zw.CreateHeader(fh)
	must(err)
	_, err = wr.Write([]byte(content))
	must(err)
	must(zw.Close())
	must(f.Close())
}

func main() {
	if len(os.Args) != 2 {
		panic("usage: go run . <workdir>")
	}
	w := os.Args[1]
	d := func(name string) string { return filepath.Join(w, name) }

	// A: link text differs (a.txt vs b.txt); resolved bytes are identical.
	writeFile(d("A1"), "a.txt", "same\n")
	writeFile(d("A1"), "b.txt", "same\n")
	makeLink(d("A1"), "link.txt", "a.txt")
	writeFile(d("A2"), "a.txt", "same\n")
	writeFile(d("A2"), "b.txt", "same\n")
	makeLink(d("A2"), "link.txt", "b.txt")
	fmt.Printf("A identity: A1(link->a.txt)=%s\n", h1(d("A1")))
	fmt.Printf("A identity: A2(link->b.txt)=%s\n", h1(d("A2")))
	fmt.Printf("A identity: equal=%t\n", h1(d("A1")) == h1(d("A2")))
	fmt.Printf("A names:    %s\n", names(d("A1")))

	// B: a link to a regular file hashes like a regular file with the same bytes.
	writeFile(d("B1"), "a.txt", "same\n")
	makeLink(d("B1"), "link.txt", "a.txt")
	writeFile(d("B2"), "a.txt", "same\n")
	writeFile(d("B2"), "link.txt", "same\n")
	fmt.Printf("B follow:   B1(link->a.txt)=%s\n", h1(d("B1")))
	fmt.Printf("B follow:   B2(regular copy)=%s\n", h1(d("B2")))
	fmt.Printf("B follow:   equal=%t\n", h1(d("B1")) == h1(d("B2")))

	// C: a retarget to a file with different bytes changes the hash.
	writeFile(d("C1"), "a.txt", "one\n")
	writeFile(d("C1"), "b.txt", "two\n")
	makeLink(d("C1"), "link.txt", "a.txt")
	writeFile(d("C2"), "a.txt", "one\n")
	writeFile(d("C2"), "b.txt", "two\n")
	makeLink(d("C2"), "link.txt", "b.txt")
	fmt.Printf("C retarget: C1(link->a.txt)=%s\n", h1(d("C1")))
	fmt.Printf("C retarget: C2(link->b.txt)=%s\n", h1(d("C2")))
	fmt.Printf("C retarget: equal=%t\n", h1(d("C1")) == h1(d("C2")))

	// D: dangling link.
	writeFile(d("D"), "a.txt", "x\n")
	makeLink(d("D"), "dangle.txt", "missing.txt")
	fmt.Printf("D dangling: %s\n", h1(d("D")))
	fmt.Printf("D names:    %s\n", names(d("D")))

	// E: link to a directory.
	writeFile(d("E"), "sub/inner.txt", "inner\n")
	makeLink(d("E"), "dirlink", "sub")
	fmt.Printf("E dir-link: %s\n", h1(d("E")))
	fmt.Printf("E names:    %s\n", names(d("E")))

	// F: the root itself is a symlink.
	writeFile(d("F"), "a.txt", "x\n")
	must(os.Symlink(d("F"), d("Froot")))
	fmt.Printf("F root-link: %s\n", h1(d("Froot")))

	// G: module-zip producers omit links.
	cf, err := xzip.CheckDir(d("B1"))
	fmt.Printf("G CheckDir(B1): err=%v valid=%v\n", err, cf.Valid)
	for _, o := range cf.Omitted {
		fmt.Printf("G   omitted %s: %v\n", filepath.Base(o.Path), o.Err)
	}
	var buf bytes.Buffer
	err = xzip.CreateFromDir(&buf, mod, d("B1"))
	fmt.Printf("G CreateFromDir(B1): err=%v\n", err)
	zr, zerr := zip.NewReader(bytes.NewReader(buf.Bytes()), int64(buf.Len()))
	must(zerr)
	for _, f := range zr.File {
		fmt.Printf("G   zip entry %s mode=%s\n", f.Name, f.Mode())
	}

	// H: a zip entry in symlink mode passes CheckZip; HashZip hashes its stored
	// text; Unzip writes it as a regular file.
	mkZip(d("zip-symlink.zip"), true, "a.txt")
	mkZip(d("zip-regular.zip"), false, "a.txt")
	_, cerr := xzip.CheckZip(mod, d("zip-symlink.zip"))
	fmt.Printf("H CheckZip(symlink-mode entry): err=%v\n", cerr)
	hs, herr := dirhash.HashZip(d("zip-symlink.zip"), dirhash.Hash1)
	hr, rerr := dirhash.HashZip(d("zip-regular.zip"), dirhash.Hash1)
	fmt.Printf("H HashZip: symlink-mode=%s err=%v\n", hs, herr)
	fmt.Printf("H HashZip: regular=%s err=%v equal=%t\n", hr, rerr, hs == hr)
	uerr := xzip.Unzip(d("unz"), mod, d("zip-symlink.zip"))
	fmt.Printf("H Unzip: err=%v\n", uerr)
	if uerr == nil {
		fi, lerr := os.Lstat(d("unz/link.txt"))
		must(lerr)
		b, rerr2 := os.ReadFile(d("unz/link.txt"))
		must(rerr2)
		fmt.Printf("H Unzip result: mode=%s symlink=%t content=%q\n", fi.Mode(), fi.Mode()&fs.ModeSymlink != 0, string(b))
	}
}
