\newcommand{\journalclass}{sagej.cls}
\newcommand{\journalclassshort}{sagej}

\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{sagej}


\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}
\ProcessOptions
\LoadClass{article}

\RequirePackage{times}
\usepackage[scaled=.95]{helvet}

\usepackage[utf8]{inputenc}
\usepackage{pifont}
\RequirePackage{graphicx}
\RequirePackage{latexsym,ifthen,rotating,calc,textcase,booktabs,color,endnotes}
\RequirePackage{amsfonts,amssymb,amsbsy,amsmath,amsthm,physics}
\RequirePackage{bm,csquotes,xcolor}
\RequirePackage[errorshow]{tracefnt}
\usepackage[inline]{enumitem}
\usepackage{moreverb,url}

\DeclareGraphicsRule{.ai}{pdf}{.ai}{}

\definecolor{tudelft-cyan}{cmyk}{1,0,0,0}
\definecolor{tudelft-petrol}{RGB}{97,164,180}
\definecolor{mpl-darkblue}{RGB}{12, 35, 64}
\definecolor{mpl-red}{RGB}{165, 0, 52}
\definecolor{mpl-lightblue}{RGB}{0, 166, 214}
\definecolor{mpl-pink}{RGB}{239, 96, 163}
\definecolor{mpl-yellow}{RGB}{255, 184, 28}
\definecolor{mpl-orange}{RGB}{236, 104, 66}

\usepackage[colorlinks,bookmarksopen,bookmarksnumbered,citecolor=tudelft-petrol,urlcolor=tudelft-petrol,linkcolor=tudelft-petrol]{hyperref}
\usepackage[noabbrev,capitalise]{cleveref}
\newcommand\BibTeX{{\rmfamily B\kern-.05em \textsc{i\kern-.025em b}\kern-.08em T\kern-.1667em\lower.7ex\hbox{E}\kern-.125emX}}
\bibliographystyle{template/SageV}

\usepackage[acronym,nonumberlist,nopostdot,nogroupskip]{glossaries}
\usepackage{glossary-inline}
\renewcommand*{\glossarysection}[2][]{\textbf{#1}: }
\glsdisablehyper

% \@twosidetrue
\flushbottom
\frenchspacing

\let\sagesf\sf


\usepackage[text={174mm,258mm},%
papersize={210mm,297mm},%
columnsep=12pt,%
headsep=21pt,%
centering]{geometry}
\usepackage{ftnright}


\parindent 1em
% \parskip 0pt

\hyphenpenalty=1000
\pretolerance=8000
\tolerance=9500
\hbadness=8000
\vbadness=9000
\displaywidowpenalty=0
\clubpenalty=10000
\widowpenalty=10000
\lefthyphenmin=3%
\righthyphenmin=3%
\brokenpenalty=10000%

\thinmuskip = 3mu
\medmuskip = 4mu
\thickmuskip = 5mu

\setcounter{topnumber}{10}
\def\topfraction{1}
\setcounter{bottomnumber}{10}
\def\bottomfraction{0.8}
\setcounter{totalnumber}{10}
\def\textfraction{0}
\renewcommand{\floatpagefraction}{0.95}
\setcounter{dbltopnumber}{10}
\renewcommand{\dblfloatpagefraction}{0.95}
\renewcommand{\dbltopfraction}{1}

\renewcommand\small{%
   \@setfontsize\small\@ixpt{10.5}%
   \abovedisplayskip 8.5\p@ \@plus3\p@ \@minus4\p@
   \abovedisplayshortskip \z@ \@plus2\p@
   \belowdisplayshortskip 4\p@ \@plus2\p@ \@minus2\p@
   \def\@listi{\leftmargin\leftmargini
               \topsep 4\p@ \@plus2\p@ \@minus2\p@
               %\parsep 2\p@ \@plus\p@ \@minus\p@
               \itemsep \parsep}%
   \belowdisplayskip \abovedisplayskip
}
\newcommand{\refsize}{\fontsize{9}{12pt}\selectfont}
\renewcommand{\footnotesize}{\fontsize{8}{10pt}\selectfont}
\renewcommand{\scriptsize}{\fontsize{7.0}{8.5pt}\selectfont}
\renewcommand{\large}{\fontsize{12}{14pt}\selectfont}
\newcommand{\titlesize}{\fontsize{18.0}{20pt}\selectfont}

\newbox\absbox
\def\abstract{\lrbox\absbox\minipage{\textwidth}%
  \sagesf\normalsize%
  \section*{\normalsize Abstract}\vskip -1.5mm%
  }
\def\endabstract{\endminipage\endlrbox}

\def\keywords#1{%
  \gdef\@keywords{\begin{minipage}{\textwidth}{\normalsize\sagesf \textbf{Keywords}}\\ \parbox[t]{\textwidth}{#1}\end{minipage}}}
\let\@keywords\@empty

\skip\footins 20pt plus  8pt
%\gdef\footnoterule{}
\def\footnoterule{\kern-3\p@
  \hrule \@width \columnwidth \kern 3mm}

\renewcommand{\thefootnote}{\arabic{footnote}}
\long\def\@makefntext#1{\parindent 1em%
\noindent{$\m@th^{\@thefnmark}$}#1}

\newcommand{\email}[1]{%
  \gdef\@email{%
\footnotetext[0]{\sagesf Email: #1}}}
\let\@email\@empty

\def\corrauth#1{\gdef\@corrauth{%
\footnotetext[0]{\par\vskip-3pt\sagesf\noindent\textbf{Corresponding author:}\\ #1}}}
\let\@corrauth\@empty

\def\affiliation#1{%
  \gdef\@affiliation{#1}
  }
\let\@affiliation\@empty

\def\affilnum#1{${}^{\text{{#1}}}$}

\renewcommand\maketitle{\par
  \begingroup
    \ifnum \col@number=\@ne
      \@maketitle
    \else
      \twocolumn[\@maketitle]%
      \fi
    \thispagestyle{title}\label{FirstPage}\@email%
  \endgroup
  %\setcounter{footnote}{0}%
    \global\let\affiliation\relax
   \global\let\thanks\relax
  \global\let\maketitle\relax
  \global\let\@maketitle\relax
  \global\let\@thanks\@empty
  \global\let\@author\@empty
  \global\let\@date\@empty
  \global\let\@title\@empty
  \global\let\@affiliation\@empty
  \global\let\title\relax
  \global\let\author\relax
  \global\let\date\relax
  \global\let\and\relax
}
\def\@maketitle{%
\vspace*{-34pt}%
\null%
\begin{center}
\begin{sf}
\begin{minipage}[t]{\textwidth}
  \vskip 12.5pt%
    {\raggedright\titlesize\textbf{\@title} \par}%
    \vskip 1.5em%
    \vskip 12.5mm%
    \end{minipage}
{\par\large%
      \lineskip .5em%
      {\raggedright\textbf{\@author}%
      \\ \textit{\small\@affiliation\@corrauth}
      \par}}
     \vskip 40pt%
    {\noindent\usebox\absbox\par}
    {\vspace{20pt}%
      %
      {\noindent\normalsize\@keywords}\par}
      \end{sf}
      \end{center}
      \vspace{22pt}
        \par%
  }
 
\def\startpage{\pageref{FirstPage}}
\def\endpage{\pageref{LastPage}}
\def\volumeyear{0000}
\def\volumenumber{XX}
\def\issuenumber{X}
\def\journalname{Journal Title}

\def\runninghead#1{\markboth{{#1}}{}}

\def\ps@title{%
\def\@oddhead{\parbox{\textwidth}{\mbox{}\\[-1pt]%
\noindent\rule{\textwidth}{0.5pt}%
}}%
\let\@evenhead\@oddhead
\def\@oddfoot{}
\let\@evenfoot\@oddfoot
}

\def\ps@sagepage{%
\let\@mkboth\@gobbletwo
\def\@evenhead{\parbox{\textwidth}{%
\normalsize\sagesf\thepage\hfil\\[-6pt]
\noindent\rule{\textwidth}{0.25pt}}}
\def\@oddhead{\parbox{\textwidth}{%
\normalsize\sagesf{\itshape{\leftmark}}\hfill\thepage\\[-6pt]
\noindent\rule{\textwidth}{0.25pt}}}
\def\@oddfoot{}
\let\@evenfoot\@oddfoot
}

%\renewcommand{\@seccntformat}[1]{{\csname the#1\endcsname.}\hspace{0.5em}}
\setcounter{secnumdepth}{2}

\newdimen\@bls                              
\@bls=\baselineskip

\renewcommand\section{\@startsection {section}{1}{\z@}%
                                   {1.2\@bls  plus .3\@bls minus .1\@bls}%
                                   {5pt\@afterindentfalse}%
                                   {\sagesf\large\bfseries\raggedright}}
\renewcommand\subsection{\@startsection{subsection}{2}{\z@}%
                                     {0.9\@bls plus .3\@bls minus .1\@bls}%
                                     {4pt\@afterindentfalse}%
                                     {\sagesf\normalsize\bfseries\raggedright}}
\renewcommand\subsubsection{\@startsection{subsubsection}{3}{\z@}%
                                     {0.5\@bls plus .3\@bls minus .1\@bls}%
                                     {-0.5em\@afterindentfalse}%
                                     {\sagesf\normalsize\itshape}}
\renewcommand\paragraph{\@startsection{paragraph}{4}{1em}%
                                     {0.3\@bls plus .3\@bls minus .1\@bls}%
                                     {-0.5em\@afterindentfalse}%
                                     {\sagesf\small\bfseries}}

% \def\enumerate{\ifnum \@enumdepth >3 \@toodeep\else
%       \advance\@enumdepth \@ne
%       \edef\@enumctr{enum\romannumeral\the\@enumdepth}\list
%       {\csname label\@enumctr\endcsname}{\usecounter
%         {\@enumctr}\itemsep 0pt\parsep 0pt
%          \def\makelabel##1{\hss\llap{##1}}}\fi}

% \let\endenumerate =\endlist

\def\itemize{\ifnum \@itemdepth >3 \@toodeep\else \advance\@itemdepth \@ne
\edef\@itemitem{labelitem\romannumeral\the\@itemdepth}%
\list{\csname\@itemitem\endcsname}{\itemsep 0pt\parsep 0pt
\def\makelabel##1{\hss\llap{##1}}}\fi}

\let\enditemize =\endlist

\RequirePackage{caption}
\DeclareCaptionLabelSeparator{sageperiod}{.\hspace*{1ex}}
\captionsetup[figure]{font=small,labelfont={sf,bf},textfont=sf,labelsep=sageperiod,justification=raggedright,singlelinecheck=false}
\captionsetup[table]{position=top,labelsep=sageperiod,font=small,labelfont={sf,bf},textfont=sf,justification=raggedright,skip=2pt,singlelinecheck=false}
\usepackage{subcaption}


\def\thmhead@plain#1#2#3{%
  \thmname{#1}\thmnumber{\@ifnotempty{#1}{ }{#2}}%
  \thmnote{ {\the\thm@notefont #3. }}}
  
\newenvironment{acks}[1]%
{\subsection*{\normalsize\sagesf\bfseries Acknowledgements}\begin{refsize}\noindent #1}%
{\end{refsize}}

\newenvironment{funding}[1]%
{\subsection*{\normalsize\sagesf\bfseries Funding}\begin{refsize}\noindent #1}%
{\end{refsize}}

\newenvironment{sm}[1]%
{\subsection*{\normalsize\sagesf\bfseries Supplemental material}\begin{refsize}\noindent #1}%
{\end{refsize}}
 
\newenvironment{dci}[1]%
{\subsection*{\normalsize\sagesf\bfseries Declaration of conflicting interests}\begin{refsize}\noindent #1}%
{\end{refsize}} 

\newenvironment{biog}[1]%
{\subsection*{\normalsize\sagesf\bfseries Author biography}\begin{refsize}\noindent #1}%
{\end{refsize}}

\newenvironment{biogs}[1]%
{\subsection*{\normalsize\sagesf\bfseries Author Biographies}\begin{refsize}\noindent #1}%
{\end{refsize}}
  
%Endnotes
\def\enotesize{\refsize}

\def\enoteheading{\subsection*{\normalsize\sagesf\bfseries\notesname}%
  \mbox{}\par\vskip-\baselineskip}

%\renewcommand\makeenmark{\theenmark.\hspace{0.75em}}

\renewcommand{\enoteformat}{%
   \rightskip\z@ \leftskip15pt \parindent=0pt
   \leavevmode{\makebox[0cm][r]{%
   \hbox to15pt{\@theenmark.\hfill}}}}
 

\usepackage[
	backend=biber,
	bibwarn=true,
	bibencoding=utf8,
	sortlocale=en_US,
	url=false,
	style=ieee-custom,
  citestyle=numeric-comp,
  isbn=false
]{biblatex}
\DeclareFieldFormat{labelnumberwidth}{#1\adddot\midsentence}

\AtBeginBibliography{\refsize}

\addbibresource{../references/bibliography.bib}

\usepackage[activate={true,nocompatibility},final,tracking=true,kerning=true,spacing=true,factor=1100,stretch=10,shrink=10]{microtype}
\SetProtrusion{encoding={*},family={bch},series={*},size={6,7}}
			     {1={ ,750},2={ ,500},3={ ,500},4={ ,500},5={ ,500},
	             6={ ,500},7={ ,600},8={ ,500},9={ ,500},0={ ,500}}
\SetExtraKerning[unit=space]
   				{encoding={*}, family={bch}, series={*}, size={notesize,small,normalsize}}
				{\textendash={400,400}, % en-dash, add more space around it
	               "28={ ,150}, % left bracket, add space from right
	               "29={150, }, % right bracket, add space from left
					\textquotedblleft={ ,150}, % left quotation mark, space from right
					\textquotedblright={150, }} % right quotation mark, space from left
\SetExtraKerning[unit=space]
				{encoding={*}, family={qhv}, series={b}, size={large,Large}}
				{1={-200,-200}, \textendash={400,400}}
\SetTracking{encoding={*}, shape=sc}{40}
\microtypecontext{spacing=nonfrench}

\usepackage{siunitx}
\sisetup{
  detect-all,
  per-mode=symbol,
  propagate-math-font,
  mode=math,
  separate-uncertainty=true,
  multi-part-units=single,
  % inter-unit-product=\ensuremath{{}\cdot{}}
}

\DeclareSIUnit{\irr}{\W\per\square\m}
\DeclareSIUnit{\acc}{\m\per\square\s}
\DeclareSIUnit{\vel}{\m\per\s}
\AtBeginDocument{\RenewCommandCopy\qty\SI}

% \renewcommand\thesubfigure{(\alph{subfigure})}
% \captionsetup[subfigure]{subrefformat=simple,labelformat=simple}

\usepackage{tabularx}
\usepackage{tablefootnote}

\AtEndDocument{%
\label{LastPage}}

\pagestyle{sagepage}

\twocolumn

\normalsize
\sloppy
