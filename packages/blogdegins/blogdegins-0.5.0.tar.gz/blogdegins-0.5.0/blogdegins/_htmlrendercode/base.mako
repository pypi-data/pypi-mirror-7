<%!
from ginsfsm.compat import iteritems_
%>
<!DOCTYPE html>
<!--[if lt IE 7]>      <html class="no-js lt-ie9 lt-ie8 lt-ie7"> <![endif]-->
<!--[if IE 7]>         <html class="no-js lt-ie9 lt-ie8"> <![endif]-->
<!--[if IE 8]>         <html class="no-js lt-ie9"> <![endif]-->
<!--[if gt IE 8]><!--> <html class="no-js"> <!--<![endif]-->
<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
    <title>${title}</title>

    <link rel="shortcut icon" href="favicon.ico"/>
    <link rel="apple-touch-icon" href="apple-touch-icon.png"/>

% for key, value in iteritems_(metadata):
    % if value:
    <meta name="${key}" content="${value}">
    % endif
% endfor

    <!-- Mobile viewport optimized: h5bp.com/viewport -->
    <meta name="viewport" content="width=device-width, initial-scale=1">

% for url in assets_env['css'].urls():
    <link rel="stylesheet" href="${url}">
% endfor

% for url in assets_env['top_js'].urls():
    <script src="${url}"></script>
% endfor

</head>

<body>

##-----------------------------------##
##         IE6,7 warning
##-----------------------------------##
<!--[if lt IE 8]>
<div style="border: 1px solid red; margin: 1em; padding: 1em; background-color: #FDD;">
<strong>Atenci&oacute;n:</strong> Est&aacute; usted utilizando una versi&oacute;n <em>obsoleta</em> de Internet Explorer. Dicha versi&oacute;n est&aacute; <em>descatalogada</em> por Microsoft y puede suponer <em>un serio riesgo para su sistema</em>, adem&aacute;s de no mostrar correctamente las p&aacute;ginas por las que navegue.<br/><h1>Esta aplicaci&oacute;n no es compatible con IExplorer 6/7.</h1>
</div>
<![endif]-->

<div id="global-grid-container" class="grid-container-class-100">
${content}
</div>

<!-- JavaScript at the bottom for fast page loading -->
% for url in assets_env['bottom_js'].urls():
<script src="${url}"></script>
% endfor

</body>
</html>
