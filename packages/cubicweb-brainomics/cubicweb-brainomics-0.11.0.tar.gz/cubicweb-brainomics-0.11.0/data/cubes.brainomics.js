
cw.cubes.brainomics = new Namespace('cw.cubes.brainomics');

$.extend(cw.cubes.brainomics, {
    getCurrentRql: function(){
	// XXX This should be done in a more easier way...
	var divid = 'pageContent';
	var vidargs = '';
	// Get facet rql
	//jQuery(CubicWeb).trigger('facets-content-loading', [divid, '', '', vidargs]);
	var $form = $('#' + divid + 'Form');
	if ($form.length != 0){
	    var zipped = facetFormContent($form);
	    zipped[0].push('facetargs');
	    zipped[1].push(vidargs);
	    return zipped;}
	else{return null;}
    },

    changeDownloadUrls: function(){
	/* Change the download urls for facet rql */
	var zipped = cw.cubes.brainomics.getCurrentRql();
	var d = loadRemote(AJAX_BASE_URL, ajaxFuncArgs('filter_build_rql', null, zipped[0], zipped[1]));
	d.addCallback(function(result) {
		    var rql = result[0];
		    $.each($('.download-ctx'), function(index, value){
			    this.href = BASE_URL+'?rql='+rql+'&vid='+this.id;
			    console.log(BASE_URL+'?rql='+rql+'&vid='+this.id);});
		    });
	},

    addDynamicFacet: function(selid){
	/* Change the download urls for facet rql */
        var $select = $("#" + selid);
	var vocabulary = $select.val();
	var zipped = cw.cubes.brainomics.getCurrentRql();
        var extraparams = {};
	extraparams['rql'] =  zipped[1][zipped[0].indexOf('baserql')];
	extraparams['vid'] = 'dynamic-facet';
	extraparams['vocabulary'] = vocabulary;
	extraparams['dynamic-facet-id'] = selid;
        var form = $select.parents('form')[0];
        var d = $('#dynamic-facet-container').loadxhtml(AJAX_BASE_URL, ajaxFuncArgs('view', extraparams));
        d.addCallback(function() {
            $(CubicWeb).trigger('dynamics-facets-added', [form]);
        });
        return false;
    },

    updateFacets: function(event, form){
        var facetargs = $(form).attr('cubicweb:facetargs');
        if (facetargs != undefined) {
            buildRQL.apply(null,  cw.evalJSON(facetargs));
        }
    }
});

$(document).ready(function() {
    $(CubicWeb).bind('dynamics-facets-added', cw.cubes.brainomics.updateFacets);
});