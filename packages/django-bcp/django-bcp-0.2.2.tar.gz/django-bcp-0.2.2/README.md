# Barcode Printer for Django

This is a reusable Django application which generates PDF barcodes in various formats with a human and machine (OCR-A) readable textual label.

These barcodes are rendered as a PDF with embedded JavaScript which prompts the PDF to be immediately printed.

Currently this is used by [Adlibre DMS](http://www.adlibre.com.au/adlibre-dms/) for document barcode generation, 
but this application is generic and can be reused in any Django app that requires barcode printing.

[ReportLab](http://www.reportlab.com) is used for the barcode generation. And the following formats are supported:

 * Code39 (3 of 9),
 * Code128.

However it would be trivial to add support for any format that ReportLab supports.

## Example

Barcode automatically printing from URL:

![Barcode Printer for Django - Automatic Printing](https://github.com/adlibre/django-bcp/raw/master/docs/example.png)

## Installation

If you use pip then the dependencies and requirements will be taken care of:

Prod:

    pip install git+git://github.com/adlibre/django-bcp.git

Dev:

    pip install -e git+git@github.com:adlibre/django-bcp.git#egg=bcp

## N.B. ReportLab Bug

ReportLab 2.5/2.6 has a typo. "OpenActions" should be "OpenAction" as per ISO 32000-1:2008.

<pre>
diff -r broken/lib/python2.7/site-packages/reportlab/pdfbase/pdfdoc.py fixed/lib/python2.7/site-packages/reportlab/pdfbase/pdfdoc.py
1022c1022
&lt;         Dests Outlines Pages Threads AcroForm Names OpenActions PageMode URI
---
&gt;         Dests Outlines Pages Threads AcroForm Names OpenAction PageMode URI
</pre>

You will need to manually patch this, otherwise the barcode will not automatically print:

    sed -i -e 's@OpenActions@OpenAction@g' lib/python*/site-packages/reportlab/pdfbase/pdfdoc.py
