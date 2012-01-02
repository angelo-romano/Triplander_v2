(function ($) {

	$.slugify = function(v) {
		if (!v) return '';
		var from = "ıİöÖüÜçÇğĞşŞâÂêÊîÎôÔûÛĘęÓóĄąŚśŁłŻżŹźĆćŃń";
		var to   = "iIoOuUcCgGsSaAeEiIoOuUEeOoAaSsLlZzZzCcNn";
		
		for (var i=0, l=from.length ; i<l ; i++) {
		    v = v.replace(from.charAt(i), to.charAt(i));
		}
	
		return v.replace(/'/g, '').replace(/\s*&\s*/g, ' and ').replace(/[^A-Za-z0-9]+/g, '-').replace(/^-|-$/g, '').toLowerCase();
	};
    
})(jQuery);