txt2pdf
=======

Text to PDF converter with Unicode support.

This is a Python 2 / 3 script using the ReportLab module for generating PDF
documents. It is intended to be used with monospace True Type fonts.
It can be hacked for being used with Type 1 Postscript fonts, but such
fonts contain less characters than TTF ones.

Usage
-----

Type the following command for getting some help:

    txt2pdf -h

The easiest way to use the tool for creating an _output.pdf_ document is:

    txt2pdf document.txt

You can change the name of the resulting PDF file:

    txt2pdf -o document.pdf document.txt

You can specify your own TTF font:

    txt2pdf -f /usr/share/fonts/ubuntu/UbuntuMono-R.ttf -o document.pdf document.txt

Other options allow to set the margins, and to adjust typographical settings (horizontal space between consecutive characters or vertical space between lines). You may also include the name of the author of the document or its title in the properties of the PDF document.

Fonts
-----

The following fonts have been tested with success:

  * Courier (by default)
  * LiberationMono
  * DejaVuSansMono
  * UbuntuMono
  * FreeMono
  * DroidSansMono
  * FiraMono
  * InputMono (different versions)
  * Envy Code
  * Anonymous Pro
  * APL385
  * APLX Unicode
  * SImPL
  * Pragmata Pro
  * Hack

The Type 1 font "Courier10PitchBT-Roman" can be used by hacking the code.

No Open Type font work, which includes:

  * Source Code Pro
  * Inconsolata
  * UMTypewriter
