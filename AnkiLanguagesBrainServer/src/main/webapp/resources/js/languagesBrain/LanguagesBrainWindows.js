
$(function () {
	
	"use strict";
	
	$.LanguagesBrainWindows = function(id) {
		
		this.loadData();
		
		this.final("id", id);
		this.final("root", $(id));
		
		this.final("menu", new $.LanguagesBrainSideMenu(this, this.root.find("aside"), this.data));
		this.final("contentElem", this.root.find("> section"));
		
		Object.preventExtensions(this);
	};
	
	$.LanguagesBrainWindows.prototype.loadData = function() {
		this.rowData = "{\"languages\":[{\"id\":1,\"name\":\"English\",\"deck\":{\"name\":\"Sentences\",\"desc\":\"Sentences list\"}},{\"id\":2,\"name\":\"\u65E5\u672C\u8A9E\"}],\"settings\":[[1,2],[\"4\",\"6\"],[{\"id\":3}]]}";
		this.data = JSON.parse(this.rowData);
	};
	
	$.LanguagesBrainWindows.prototype.show = function() {
		this.menu.show();
	};
	
	/**
	 * Menu
	 */
	
	$.LanguagesBrainSideMenu = function(parent, elem, data) {
		
		this.languages = languages = [];
		data.languages.forEach(function (d){languages.push(new $.Language(d))});
			
		this.final("parent", parent);
		this.final("elem", elem);
		
		this.currentLanguage = null;
		
		this.final("languagesElem", elem.find("#languages"));
		this.final("addNewLanguageBtn", elem.find("#addNewLanguageBtn"));
		this.final("menuElem", elem.find("#menu"));
		
		this.final("infoElem", this.menuElem.find("#info"));
		this.final("browserElem", this.menuElem.find("#browser"));
		
		this.addNewLanguageBtn.click(function () {
			console.log("hellow");
			return false;
		});
		
		this.browserElem.click(function () {
			console.log("hellow");
			return false;
		});
		
		this.infoElem.click(function (e) {
			console.log("click");
			return false;
		});
		
		Object.preventExtensions(this);
	};
	
	$.LanguagesBrainSideMenu.prototype.addNewLanguage = function(id, name) {
		var language = new $.Language({"id" : id, "name" : name});
		this.languages.push(language);			
		return language;
	};
	
	
	$.LanguagesBrainSideMenu.prototype.removeMenu = function() {
		this.menuElem.hide();
		this.elem.parent().append(this.menuElem);
	};
	
	$.LanguagesBrainSideMenu.prototype.show = function() {
		var instance = this,
			len,
			i,
			span,
			li,
			language;
		
		this.removeMenu();
		this.languagesElem.html("");
		
		for (i = 0, len = this.languages.length; i < len; i += 1) {
			language = this.languages[i];
			
			li = $("<li />");
			span = li.append($("<span />"));
			
			li.attr("language-id", language.id);
			span.html(language.name);
			span.data("language", language);

			if (this.currentLanguage && this.currentLanguage.id === language.id) {
				li.addClass("active");
				li.append(this.menuElem);

				this.menuElem.show();
			} 
			
			span.click(function (e) {
				var toLanguage = $(e.target).data("language");
				if (instance.currentLanguage && instance.currentLanguage.id === toLanguage.id) {
					instance.currentLanguage = null;
				} else {
					instance.currentLanguage = toLanguage;
				}
				instance.show();
			});
			
			this.languagesElem.append(li);
		}
	};
	
	/**
	 * Language
	 */
	
	$.Language = function(data) {
		
		if (!(this instanceof $.Language)) {
			return new $.Language(data);
		}
		
		this.final("id", data.id);
		this.final("name", data.name);
		
		Object.preventExtensions(this);
	};

	
	

	
});