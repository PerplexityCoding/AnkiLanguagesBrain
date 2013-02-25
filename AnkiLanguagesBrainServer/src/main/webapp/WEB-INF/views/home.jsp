<%@page contentType="text/html" pageEncoding="UTF-8"%>
<!DOCTYPE HTML>

<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
        <title>Home</title>
        
        <link href="resources/css/normalize.css" rel="stylesheet"> 
        <link href="resources/css/style.css" rel="stylesheet"> 
        
        <script src="//ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>
        <script src="//ajax.googleapis.com/ajax/libs/jqueryui/1.10.1/jquery-ui.min.js"></script>
        
        <script src="resources/js/utils/utils.js"></script>
        
        <script src="resources/js/languagesBrain/LanguagesBrainWindows.js"></script>
        
        <script>
        	$(function () {
        		var windows = new $.LanguagesBrainWindows("#mainWindows");
        		
        		windows.show();   
        		
        		
        		$("#mainWindows").draggable();
        		$("#mainWindows").resizable();
        	});
        </script>
        
    </head>
    <body>
        <div id="mainWindows">
        	<aside>
        		<ul id="menu" class="hidden">
        			<li id="info">Info</li>
        			<li id="browser">Morphemes Browser</li>
        		</ul>        	
        		<ul id="languages">
        		</ul>
        		<div id="addNewLanguageBtn">
        			<span>Add a new Language</span>
        			<div id="newLanguageMenu" class="hidden">
        				<select>
        					<option value="1">English</option>
        					<option value="2">Dutch</option>
        				</select>
        				<span class="button bKO" id="newLanguageCancel">Cancel</span>
        				<span class="button bOK" id="newLanguageDone">Done</span>
        			</div>
        		</div>        		
        	</aside>
        	<section></section>
        </div>
    </body>
</html>
