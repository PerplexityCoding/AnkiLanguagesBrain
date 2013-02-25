$.BindingArray = function (array, binder) {
	var i, len;
	
	if (!(this instanceof $.BindingArray)) {
		return new $.BindingArray(array, binder);
	}
	
	if (array) {
	
		this.data = array;	
		this.binder = binder;
		this.length = 0;
		
		for (i = 0, len = array.length; i < len; i += 1) {				
			if (binder) {
				this[this.length] = new binder(array[i]);
			} else {
				this[this.length] = array[i];			
			}
			this.length += 1;
		}
	} else {
		this.data = [];
		this.length = 0;
	}
};

$.BindingArray.prototype.push = function (elem) {
	this[this.length] = elem;
	this.length += 1;
	
	if (elem.data) {
		this.data.push(elem.data);
	} else {
		this.data.push(elem);
	}
	
	this.changed = true;
};

$.BindingArray.prototype.remove = function (elem) {
	var i = 0,
		j = 0,
		found = false,
		len = this.length;
	
	for (i = 0; i < len; i += 1) {
		if (this[i] === elem) {
			found = true;
			break;
		}
	}
	
	if (found) {
		this.data.splice(i, 1);
		for (j = i + 1; j < len; j += 1) {
			this[j - 1] = this[j];
		}
		delete this[j - 1];
		this.length -= 1;
		
		this.changed = true;
	}		
};

$.DataBinder = function (o, data) {
	
	o.data = data;

	Object.defineProperty(o, "bind", { 
		enumerable: false,
		value : function (key, data, binder, loadData) {
			
			if (Array.isArray(data)) {
				
				(function (o, key, data, binder) {
				
					var array = null;
					if (data) {
						array = new $.BindingArray(data, binder);
					}
					
					Object.defineProperty(o, key, {
						set : function (data) {
							o.changed = true;
							array = data;
						},
						get : function () {
							return array;
						}
					});
				
				})(o, key, data, binder);
			
			} else if (data instanceof Object) {
			
				(function (o, key, data, binder) {
				
					var bindingObject = null;
					if (data) {
						bindingObject = new binder(data);
					} 
					
					Object.defineProperty(o, key, {
						set : function (val) {
							o.changed = true;
							bindingObject = val;
						},
						get : function () {
							return bindingObject;
						}
					});
				
				})(o, key, data, binder);
				
			} else {
				(function (o, key, data) {
					
					var value = data;
					
					Object.defineProperty(o, key, {
						set : function (val) {
							o.data[key] = val;
							value = val;
							o.changed = true;
						},
						get : function () {
							return value;
						}
					});
				
				})(o, key, data);					
			}
		}
	});

	Object.preventExtensions(this);
};