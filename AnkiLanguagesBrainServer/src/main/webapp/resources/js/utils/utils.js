
function final(obj, prop, value) {
	Object.defineProperty(obj, prop, {get: function(){return value;}});
}

Object.defineProperty(Object.prototype, "final", {
	enumerable: false,
	value : function (prop, value) {
		final(this, prop, value);
	}
});