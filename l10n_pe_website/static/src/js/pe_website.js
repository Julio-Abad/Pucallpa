function validate_pe_doc(pe_doc_type, vat) {
    if (!pe_doc_type || !vat){
        return false;
    }
    if (vat.length==8 && pe_doc_type=='1') {
        return true;
    }
    else if (vat.length==11 && pe_doc_type=='6')
    {
        var vat= vat;
        var factor = '5432765432';
        var sum = 0;
        var dig_check = false;
        if (vat.length != 11){
            return false;
        }
        try{
            parseInt(vat)
        }
        catch(err){
            return false; 
        }
        
        for (var i = 0; i < factor.length; i++) {
            sum += parseInt(factor[i]) * parseInt(vat[i]);
         } 

        var subtraction = 11 - (sum % 11);
        if (subtraction == 10){
            dig_check = 0;
        }
        else if (subtraction == 11){
            dig_check = 1;
        }
        else{
            dig_check = subtraction;
        }
        
        if (parseInt(vat[10]) != dig_check){
            return false;
        }
        return true;
    }
    else if (vat.length>=3 &&  ['0', '4', '7', 'A'].indexOf(pe_doc_type)!=-1) {
        return true;
    }
    else if (pe_doc_type.length>=2) {
        return true;
    }
    else {
        return false;
    }
};
function get_partner_datas() {
	var pe_doc_type = $(".peruvian_doc_type").val();
	var pe_doc_number = $(".peruvian_doc_number").val();
	if (['1','6'].indexOf(pe_doc_type) > -1) {
		if (validate_pe_doc(pe_doc_type,pe_doc_number) == true) {
			$.ajax({ 
				url: "/website/peruviandocument/",
				data: {'pe_doc_number': pe_doc_number, 'pe_doc_type':pe_doc_type},
				dataType : 'json',
			}).done(function( data ) {
				if (pe_doc_type == '6'){
					$("input[name='name']").val(data.legal_name || '');
					$("input[name='street']").val(data.street || '');
					$("input[name='zip']").val(data.zip || '');
					$("input[name='zipcode']").val(data.zip || '');
					$("input[name='city']").val(data.district || '');
					$("select[name='country_id']").val(data.country_id || '');
					$("select[name='state_id']").val(data.state_id || '');
				}
				if (pe_doc_type == '1'){
					var name = (data.paternal_surname || '') +' '+ (data.maternal_surname || '') +', ' + (data.name || '');
					$("input[name='name']").val(name);
					$("select[name='country_id']").val(data.country_id || '');
				}
			});
		}
		else {
			alert( "El RUC o DNI no es valido" );
		}
	}

};
$(".peruvian_doc_number" ).change(function() {
	get_partner_datas();
});
