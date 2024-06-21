[![](https://img.shields.io/badge/github-purple?style=for-the-badge)](https://github.com/D4ario0/rocketpdf/) [![](https://img.shields.io/badge/Pypi-blue?style=for-the-badge)](https://pypi.org/project/rocketpdf/)
# rocketpdf
rocketpdf is python-based powerful CLI app that take basic pdf operations and elevates the user experience to the next level, allowing the user to not only convert and modify existing pdf files, but to chain operations and get a polished final result in a single swing!

This project "concatenates" efforts of different open-source solutions like `docx2pdf`, `pdf2docx` or `typer` and creates a powerful tool for quickly managing and modifying pdf files from the console. 

# Install 
``` bash
pip install rocketpdf
```
# CLI
> It is always recommended to open a terminal inside the directory you will be working.

  | Command | Description |
  | --- | --- |
  | `parsedoc` | Converts `.docx` file into `.pdf` file. |
  | `parsedocxs` | Converts all `.docx` files inside a directory into `.pdf` files. |
  | `parsepdf` | Converts `.pdf` file into `.docx` file. |
  | `merge` | Merges multiple `.pdf` files into a single`.pdf` file. |
  | `mergeall` | Merges all `.pdf` files inside a directory into a single `.pdf` file. |
  | `extract` | Extract a certain range of pages from a `.pdf` file. |
  | `compress` | Reduces the size of `.pdf` file. |
  
<details>
<summary>parsedoc</summary>
  
## parsedoc
Converts `.docx` file into `.pdf` file.
``` bash
rocketpdf parsedoc sample.docx
```
`-o`: Customize file output name. Default: `{filename}.pdf`.
</details>
<details>
<summary>parsedocxs</summary>
  
## parsedocxs
Converts all `.docx` files inside a directory into `.pdf` files.
``` bash
rocketpdf parsedocxs C:\Users\user\samples
```
Default: `{filename}.pdf`.
</details>
<details>
<summary>parsepdf</summary>
  
## parsepdf
Converts `.pdf` file into `.docx` file.
``` bash
rocketpdf parsepdf sample.pdf
```
`-o`: Customize file output name. Default: `{filename}.docx`.
</details>
<details>
<summary>merge</summary>
  
## merge
Merges multiple `.pdf` files into a single`.pdf` file.
``` bash
rocketpdf merge sample.pdf sample2.pdf sample3.pdf
```
`-o`: Customize file output name. Default: `merged.pdf`.
</details>
<details>
<summary>mergeall</summary>  

## mergeall
Merges all `.pdf` files inside a directory into a single `.pdf` file.
``` bash
rocketpdf mergeall C:\Users\user\samples
```
`-o`: Customize file output name. Default: `{directory}-merged.pdf`.
</details>
<details>
<summary>extract</summary>
  
## extract
Extract a certain range of pages from a `.pdf` file.
### Single page
``` bash
rocketpdf extract sample.pdf 2
```
### Multi-page
``` bash
rocketpdf extract sample.pdf 2 4
```
`-o`: Customize file output name. Default: `{filename} page(s) # - #`
</details>
<details>
  <summary>compress</summary>
  
## compress
Reduces the size of `.pdf` file.
``` bash
rocketpdf compress sample.pdf
```
`-o`: Customize file output name. Default: `{filename}-compressed.pdf`.
</details>

# Command chaining 
`rocketpdf` is a powerful tool that allows users to execute multiple commands in a single line by passing the binary result of a file onto the next operation.
## Use cases
To chain multiple operations it is assumed that that the previous operations file result will be the input of the next command.

Let's download all monthly invoices into `Invoices 2024` folder and `compress` the file for easier upload:
``` bash
rocketpdf mergeall ".\Invoices 2024" compress -o Invoices_2024.pdf 
```

Let's convert my `Resume.docx` to `.pdf` and append my `Cover_Letter.pdf`
``` bash
rocketpdf parsedoc Resume.docx merge Cover_Letter.pdf -o Job_Application.pdf 
```

Let's `extract` the first page of `passsport.pdf` and append my `bank_deposit_info.pdf`:
``` bash
rocketpdf extract passport.pdf 1 merge bank_deposit_info.pdf -o payment_information.pdf
```

> + `parsepdf` outputs a `.docx` file so no arguments can be chained after it.
> + `parsedoc` is generally a starting command in a chain, so it cannot be used after any other operation.
> + `parsedocxs` is not chainable.

# Compatibility 
`rocketpdf` is compatible with `_Windows_` and `_Mac_` systems with `MS Word` installed.

> Unfortunately `_Linux_` users cannot parse `.docx` files into `.pdf` files due to lack of libraries and support. The team (me) will be looking forward to bring a Linux-based solution in the near future.
