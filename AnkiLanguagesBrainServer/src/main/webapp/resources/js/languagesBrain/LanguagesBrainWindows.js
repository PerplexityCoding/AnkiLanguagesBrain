
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
		this.rowData = "{\"languages\":[{\"id\":1,\"name\":\"English\"},{\"id\":2,\"name\":\"\u65E5\u672C\u8A9E\"},{\"id\":3,\"name\":\"French\"},{\"id\":4,\"name\":\"Dutch\"}],\"current_languages\":[1,2],\"available_languages\":[3,4]}";
		this.data = JSON.parse(this.rowData);
	};
	
	$.LanguagesBrainWindows.prototype.show = function() {
		this.menu.show();
	};
	
	/**
	 * Menu
	 */
	
	$.LanguagesBrainSideMenu = function(parent, elem, data) {
		
		var that = this;
		
		this.languages = {};
		data.languages.forEach(function (e){that.languages[e.id] = new $.Language(e);});
		
		this.currentLanguages = [];
		data.current_languages.forEach(function (d){that.currentLanguages.push(that.languages[d]);});
		
		this.availableLanguages = [];
		data.available_languages.forEach(function (d){that.availableLanguages.push(that.languages[d]);});
		
			
		this.final("parent", parent);
		this.final("elem", elem);
		
		this.currentLanguage = null;
		
		this.final("languagesElem", elem.find("#languages"));
		this.final("addNewLanguageBtn", elem.find("#addNewLanguageBtn"));
		this.final("menuElem", elem.find("#menu"));
		
		this.final("infoElem", this.menuElem.find("#info"));
		this.final("browserElem", this.menuElem.find("#browser"));
		
		this.final("newLanguageDone", elem.find("#newLanguageDone"));
		this.final("newLanguageCancel", elem.find("#newLanguageCancel"));
		
		this.final("newLanguageMenu", elem.find("#newLanguageMenu"));
		this.final("newLanguageMenuSelect", this.newLanguageMenu.find("select"));
		
		this.addNewLanguageBtn.click(function (e) {
			that.newLanguageMenu.show();
			return false;
		});
		
		this.newLanguageDone.click(function (e) {
			var language = that.newLanguageMenuSelect.find("option:selected").data("language");
			if (language) {
				that.newLanguageMenu.hide();
	
				that.addNewLanguage(language);
				that.currentLanguage = language;
				that.show();						
			}
			return false;
		});
		
		this.newLanguageCancel.click(function (e) {
			that.newLanguageMenu.hide();
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
	
	$.LanguagesBrainSideMenu.prototype.addNewLanguage = function(language) {
		this.currentLanguages.push(language);
		
		var i, len;
		for (i = 0, len = this.availableLanguages; i < len; i += 1) {
			if (language.id === this.availableLanguages[i].id) {
				break;
			}
		}
		this.availableLanguages.splice(i, 1);
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
			option,
			language;
		
		this.removeMenu();
		this.languagesElem.html("");
		this.newLanguageMenuSelect.html("");
		
		if (this.availableLanguages.length > 0) {
			for (i = 0, len = this.availableLanguages.length; i < len; i += 1) {
				language = this.availableLanguages[i];
				
				option = $("<option />");
				option.attr("val", language.id);
				option.html(language.name);
				option.data("language", language);
				
				this.newLanguageMenuSelect.append(option);
			}
		} else {
			this.newLanguageMenuSelect.append("<option>No language Available</option>");
		}
		
		for (i = 0, len = this.currentLanguages.length; i < len; i += 1) {
			language = this.currentLanguages[i];
			
			li = $("<li />");
			span = li.append($("<span />"));
			
			li.attr("language-id", language.id);
			span.html(language.name);
			span.data("language", language);

			if (this.currentLanguage && this.currentLanguage.id === language.id) {
				li.addClass("active");
				li.append(this.menuElem);
				
				this.menuElem.find("li:first-child").addClass("active");

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