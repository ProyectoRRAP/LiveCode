//URLs ouers service
var HOST_NAME = 'localhost';
var PORT_NMBR = '8080';
var URL_BASE = 'http://' + HOST_NAME + ':' + PORT_NMBR;
var URI_API_REST_TOPOLOGY = URL_BASE + '/topology';
var URI_API_REST_TOPOLOGY_NODE = URI_API_REST_TOPOLOGY + '/node';
var URI_API_REST_TOPOLOGY_NODE_INTERFACE = URI_API_REST_TOPOLOGY_NODE + '/interfaces';
var URI_API_REST_TOPOLOGY_NODE_MPLS = URI_API_REST_TOPOLOGY_NODE + '/mpls';
var URI_API_REST_TOPOLOGY_NODE_MPLS_ILM = URI_API_REST_TOPOLOGY_NODE_MPLS + '/ilm';
var URI_API_REST_TOPOLOGY_NODE_MPLS_FTN = URI_API_REST_TOPOLOGY_NODE_MPLS + '/ftn';
var URI_API_REST_TOPOLOGY_NODE_MPLS_NHLFE = URI_API_REST_TOPOLOGY_NODE_MPLS + '/nhlfe';
var URI_API_REST_TOPOLOGY_DATAPATHS = URI_API_REST_TOPOLOGY + '/datapaths';
var URI_API_REST_SERVICES = URL_BASE + '/services';
var URI_API_REST_SERVICE = URI_API_REST_SERVICES + '/service';
var URI_API_REST_SERVICES_LSPS = URI_API_REST_SERVICES + '/lsps';

//URLs ryu services
var URL_RYU_BASE = 'stats';
var URL_RYU_FLOW_STATS = URL_RYU_BASE + '/flow/' /*{dpid}*/

var selectedServiceConfigTab;
var selectedNodeConfigTab;
var selectedNodeIfaceTab;
var services_data = {};
var nodes_data = {};
var services_topo_data = {};

//Saves services checked for topology services render
var srvs_render_checked = [];
var links_colors = {};

var selected_node = null;

//Graphics variables
var activeTopBarTab;
var activeMenu;

//EVENTS
$(document).ready(function(){
	activeTopBarTab = $("#tab-1-topo");
	activeTopBarTab.show();
	activeMenu = $("#topologyRenderOpt");

    $('#addServiceForm_SubmitButton').click(function(){
        processServiceForm(1);
    });
    $('#updateServiceForm_SubmitButton').click(function(){
        processServiceForm(2);
    });
    $('#addServiceButton').click(function(){
        loadDataCombosNodeIngressNodeEgress("addServiceForm");
    });
    $('#updateServiceButton').click(function(){
        if(typeof selectedServiceConfigTab == 'undefined'){
    		var mensaje = $("#errorModal_Message");
    		mensaje.empty();
    		mensaje.append("Debes seleccionar un servicio");
    		$("#errorModal").foundation('reveal', 'open');
    	}
    	else{
    		loadDataModalUpdateService(selectedServiceConfigTab);
    	}
    });
    $("#addServiceForm_IngressNode").change(function() {
    	var value = $("#addServiceForm_IngressNode").val();
		loadDataComboNodeIngressInterfaces(value, "addServiceForm", null);
	});
	$("#addServiceForm_EgressNode").change(function() {
    	var value = $("#addServiceForm_EgressNode").val();
		loadDataComboNodeEgressInterfaces(value, "addServiceForm", null);
	});
    $("#updateServiceForm_IngressNode").change(function() {
    	var value = $("#updateServiceForm_IngressNode").val();
		loadDataComboNodeIngressInterfaces(value, "updateServiceForm", null);
	});
	$("#updateServiceForm_EgressNode").change(function() {
    	var value = $("#updateServiceForm_EgressNode").val();
		loadDataComboNodeEgressInterfaces(value, "updateServiceForm", null);
	});
	$("#expandServiceButton").click(function() {
    	if(typeof selectedServiceConfigTab == 'undefined'){
			var mensaje = $("#errorModal_Message");
    		mensaje.empty();
    		mensaje.append("Debes seleccionar un servicio");
    		$("#errorModal").foundation('reveal', 'open');
    	}
    	else{
    		loadDataModalService(selectedServiceConfigTab);
    	}
	});
	$("#expandService_CloseButton").click(function() {
    	$('#serviceExpandModal').foundation('reveal', 'close');
	});

	$("#deleteServiceButton").click(function() {
    	if(typeof selectedServiceConfigTab == 'undefined'){
			var mensaje = $("#errorModal_Message");
    		mensaje.empty();
    		mensaje.append("Debes seleccionar un servicio");
    		$("#errorModal").foundation('reveal', 'open');
    	}
    	else{
    		$('#serviceDeleteConfirmModal').foundation('reveal', 'open');

    	}
	});
	$("#deleteServiceCancelButton").click(function() {
    	$('#serviceDeleteConfirmModal').foundation('reveal', 'close');
	});
	$("#deleteServiceConfirmButton").click(function() {
		deleteService(selectedServiceConfigTab);
    	$('#serviceDeleteConfirmModal').foundation('reveal', 'close');
	});

	$("#checkboxRenderServices").click(function() {
    	$('#topologyViewServiceRenderSelector').foundation('reveal', 'open');
	});
	
	$("#topologyViewServiceRenderCancelButton").click(function() {
    	$('#topologyViewServiceRenderSelector').foundation('reveal', 'close');
	});

	$("#ampliarServiceOpt").click(function() {
		var currentTab = $("#AmpliarTab");
		var currentOpt = $("#ampliarServiceOpt");
		if(activeTopBarTab != $("#tab-1-topo")){
			activeTopBarTab.hide();
		}
		activeMenu.parent().removeClass("active");

    	currentTab.show();
    	currentOpt.parent().addClass("active");
    	activeTopBarTab = currentTab;
    	activeMenu = currentOpt;

    	clearNodeDataDisplay();
    	loadNodeData(selected_node);
	});
	$("#topologyRenderOpt").click(function() {
		var currentTab = $("#tab-1-topo");
		var currentOpt = $("#topologyRenderOpt");
		if(activeTopBarTab != $("#tab-1-topo")){
			activeTopBarTab.hide();
		}
		activeMenu.parent().removeClass("active");

    	currentTab.show();
    	currentOpt.parent().addClass("active");
    	activeTopBarTab = currentTab;
    	activeMenu = currentOpt;
	});
	$("#flowsServiceOpt").click(function() {
		var currentTab = $("#flowsTab");
		var currentOpt = $("#flowsServiceOpt");
		if(activeTopBarTab != $("#tab-1-topo")){
			activeTopBarTab.hide();
		}
		activeMenu.parent().removeClass("active");

    	currentTab.show();
    	currentOpt.parent().addClass("active");
    	activeTopBarTab = currentTab;
    	activeMenu = currentOpt;

    	loadNodeFlowTable(selected_node);
	});
	$("#mplsServiceOpt").click(function() {
    	var currentTab = $("#mplsTab");
		var currentOpt = $("#mplsServiceOpt");
		if(activeTopBarTab != $("#tab-1-topo")){
			activeTopBarTab.hide();
		}
		activeMenu.parent().removeClass("active");

    	currentTab.show();
    	currentOpt.parent().addClass("active");
    	activeTopBarTab = currentTab;
    	activeMenu = currentOpt;

    	loadNodeMPLSTables(selected_node);
	});
	


	$("#topologyViewServiceRenderConfirmButton").click(function() {
		var tabla = $("#TabTopologyServiceRenderSelectorTable");
		var row;
		var chk;
		var new_srvs_render_checked = [];

		tabla.find('tr').each(function () {
        	row = $(this);
        	chk = row.find('input[type="checkbox"]');
        	if(chk.is(':checked')){
        		console.log('servicio chked');
            	new_srvs_render_checked.push(chk.val());
        	}
        });
		
		updateServicesRender(new_srvs_render_checked);
    	$("#topologyViewServiceRenderSelector").foundation('reveal', 'close');
	});

	$("#errorModal_closeButton").click(function(){
    	$("#errorModal").foundation('reveal', 'close');
    });

    $("#configTabNodesSubTab").click(function(){
    	loadConfigTabNodesSubTabData();
    });
    $("#editNodeInfoButton").click(function(){
    	if((typeof selectedNodeConfigTab == 'undefined') || (selectedNodeConfigTab == null)){
			var mensaje = $("#errorModal_Message");
    		mensaje.empty();
    		mensaje.append("Debes seleccionar un nodo");
    		$("#errorModal").foundation('reveal', 'open');
    	}
    	else{
    		loadNodeReducedInfo(selectedNodeConfigTab);
    		$("#configTabNodesSubTabEdit").foundation('reveal', 'open');
    	}
    		
    });

    $("#editNodeIfaceInfoButton").click(function(){
    	if((typeof selectedNodeIfaceTab == 'undefined') || (selectedNodeIfaceTab == null)){
			var mensaje = $("#errorModal_Message");
    		mensaje.empty();
    		mensaje.append("Debes seleccionar una interfaz");
    		$("#errorModal").foundation('reveal', 'open');
    	}
    	else{
    		loadNodeInterfaceReducedInfo(selectedNodeIfaceTab);
    		$("#configTabInterfaceSubTabEdit").foundation('reveal', 'open');
    	}
    		
    });

    //--
	$(document).on ("change", ".TabConfigServicesTableSlct", function () {
    	var value = $(this).val();
    	selectedServiceConfigTab = value;
    });

    $(document).on ("change", ".TabConfigNodesSubTabTableSlct", function () {
    	var value = $(this).val();
    	selectedNodeConfigTab = value;
    	loadNodeDataInterfaces(value);
    });

    $(document).on ("change", ".TabConfigNodesSubTabIfaceTableSlct", function () {
    	var value = $(this).val();
    	selectedNodeIfaceTab = value;
    });    

    $("#configTabNodesSubTabEditFormConfirmButton").click(function(){
    	processNodeEditForm();	
    });

    $("#configTabNodesSubTabEditFormCancelButton").click(function(){
    	$("#configTabNodesSubTabEdit").foundation('reveal', 'close');		
    });

    $("#configTabNodesInterfaceSubTabEditFormConfirmButton").click(function(){
    	processNodeInterfaceEditForm();	
    });

    $("#configTabNodesInterfaceSubTabEditFormCancelmButton").click(function(){
    	$("#configTabInterfaceSubTabEdit").foundation('reveal', 'close');		
    });

    


    //--
    $(document).on ("click", ".node", function () {
    	
    	var value = $(this).attr("id");
    	selected_node = value;
    	//var left = $(this).position().left + $(this).width()/2;
    	//var top = $(this).position().top;
    	//showMiniInfoBoxNode(value, left, top, /*$(this).width()*/51, /*$(this).height()*/57);
    });

    $(document).on ("mouseover", ".node", function () {	
    	var value = $(this).attr("id");
    	selected_node = value;
    	var left = $(this).position().left + $(this).width()/2;
    	var top = $(this).position().top;
    	showMiniInfoBoxNode(value, left, top, /*$(this).width()*/51, /*$(this).height()*/57);
    });

    $(document).on ("mouseout", ".node", function () {	
    	var value = $(this).attr("id");
    	var infoBox = $('#miniInfoBoxNode-' + value);
		var infoBoxArrow = $('#miniInfoBoxNodeArrow-' + value);
    	infoBox.hide();
		infoBoxArrow.hide();
    });


    loadTopologyData();

    loadServicesTopologyData();

    loadConfigTabServiceTabData();

 });

function loadDevicesTabData(){

	loadTopologyData();
}

function loadNodeDataInterfaces(dpid){
	console.log('llego');
	var node = nodes_data[dpid];
	var interfaces = node['interfaces'];
	var iface;

	var name;
	var ip_address;
	var mac_address;
	var ovs_port;

	var table = $("#TabConfigNodesInterfaesTable");
	table.empty();
	var table_row;

	for(i in interfaces){
		iface = interfaces[i];
		name = iface['name'];
		ip_address = iface['ip_address'];
		mac_address	= iface['mac_address'];
		ovs_port = iface['ovs_port'];

		table_row = "<tr>"
					+	"<td>" + name + "</td>"
					+	"<td>" + ip_address + "</td>"
					+	"<td>" + mac_address + "</td>"
					+	"<td>" + ovs_port + "</td>"
					+   "<td><input class='TabConfigNodesSubTabIfaceTableSlct'" 
					+       " name='NodeSlct' value='" + ip_address + "' id='' type='radio' />"
					+   "</td>" 
				+	"</tr>";

	    table.append(table_row);
	}
}

function loadNodeInterfaceReducedInfo(iface){
	var node = nodes_data[selectedNodeConfigTab];
	var iface = node['interfaces'][iface];
	var top_type = node['type'];

	if(top_type == 0){
		$("#configTabInterfaceSubTabEditForm_ifaceTopType1").attr('checked', '');
		$("#configTabInterfaceSubTabEditForm_ifaceTopType2").attr('checked', 'checked');
	}
	else{
		$("#configTabInterfaceSubTabEditForm_ifaceTopType1").attr('checked', 'checked');
		$("#configTabInterfaceSubTabEditForm_ifaceTopType2").attr('checked', '');
	}
}

function loadNodeReducedInfo(dpid){
	var node = nodes_data[dpid];
	var top_type = node['top_type'];
	var name = node['name'];

	$("#configTabNodesSubTabEditForm_nodeName").val(name);
	if(top_type == 0){
		$("#configTabNodesSubTabEditForm_nodeTopType1").attr('checked', '');
		$("#configTabNodesSubTabEditForm_nodeTopType2").attr('checked', 'checked');
	}
	else{
		$("#configTabNodesSubTabEditForm_nodeTopType1").attr('checked', 'checked');
		$("#configTabNodesSubTabEditForm_nodeTopType2").attr('checked', '');
	}
}	

function processNodeInterfaceEditForm(){
	var iface_top_type; 
	var router_id = nodes_data[selectedNodeConfigTab]['router_id'];
	var ip_address = selectedNodeIfaceTab;

	if($("#configTabInterfaceSubTabEditForm_ifaceTopType1").is(':checked')){
		node_top_type = 1;	
	}
	else if($("#configTabInterfaceSubTabEditForm_ifaceTopType2").is(':checked')){
		node_top_type = 0;	
	};

	var ce_ip_address = $("#configTabInterfaceSubTabEditForm_ifaceCEIpAddress").val();
	var ce_mac_address = $("#configTabInterfaceSubTabEditForm_ifaceCEMacAddress").val(); 
	 
	var data = {'iface_top_type': node_top_type, 'router_id': router_id, 'ip_address': ip_address, 'ce_mac_address': ce_mac_address, 
				'ce_ip_address': ce_ip_address};
	postNodeInterfaceExtraData(data, router_id, ip_address);
}

function processNodeEditForm(){
	var node_name = $("#configTabNodesSubTabEditForm_nodeName").val();
	var node_type_edge = false;
	var node_type_core =  false;
	var node_top_type; 
	var router_id = nodes_data[selectedNodeConfigTab]['router_id'];

	if($("#configTabNodesSubTabEditForm_nodeTopType1").is(':checked')){
		node_top_type = 1;	
	}
	else if($("#configTabNodesSubTabEditForm_nodeTopType2").is(':checked')){
		node_top_type = 0;	
	};
	 
	var data = {'node_name': node_name, 'node_top_type': node_top_type, 'router_id': router_id};
	postNodeExtraData(data, router_id);
}

function loadConfigTabNodesSubTabData(){
	/* Updates topology info */
	loadTopologyData(loadConfigTabNodesSubTabData_Callback);
}

function loadConfigTabNodesSubTabData_Callback(){
	var node;
	var node_name;
	var router_id;
	var datapath_id;

	var table_row;
	var table =  $("#TabConfigNodesTable");
	table.empty();

	for(key in nodes_data){
		node = nodes_data[key];
		node_name = node['name'];
		router_id = node['router_id'];
		datapath_id =  node['datapath_id'];

		table_row = "<tr>"
					+	"<td>" + node_name + "</td>"
					+	"<td>" + router_id + "</td>"
					+	"<td>" + datapath_id + "</td>"
					+   "<td><input class='TabConfigNodesSubTabTableSlct'" 
					+       " name='NodeSlct' value='" + datapath_id + "' id='' type='radio' />"
					+   "</td>" 
				+	"</tr>"	

	    table.append(table_row);
	}
}

function clearNodeDataDisplay(){
	$("#topoTabAmpliarOptInterfaces").empty();
}
function clearTopoTabInfoOpt(){
	$("#topoTabAmpliarOptNombre").empty();
	$("#topoTabAmpliarOptDPID").empty();
	$("#topoTabAmpliarOptRID").empty();
	$("#topoTabAmpliarOptDesc").empty();
	$("#topoTabAmpliarOptTipo").empty();
}

function clearEditNodeInterfacesTable(){
	var table = $("#TabConfigNodesInterfaesTable");
	table.empty();
}

function loadNodeData(node){
	var interafces;
	var inter;
	var ovs_port;
	var ip_address;
	var mac_address;

	var interfacesList = $("#topoTabAmpliarOptInterfaces");
	$.ajax({
		dataType: "json",
		url: URI_API_REST_TOPOLOGY_NODE + '/' + nodes_data[node].router_id,
		type: "GET",
		success: function(resultData) {
			console.log(resultData);
			 
	    	$("#topoTabAmpliarOptNombre").html(resultData["name"]);
	    	$("#topoTabAmpliarOptDPID").html(resultData["datapath_id"]);
	    	$("#topoTabAmpliarOptRID").html(resultData["router_id"]);
	    	$("#topoTabAmpliarOptDesc").html(resultData["description"]);
	    	$("#topoTabAmpliarOptTipo").html(resultData["top_type"]);

	    	interfaces = resultData["interfaces"];
	    	for(i in interfaces){
	    		inter = interfaces[i];
	    		i_name = inter['name'];
	    		ovs_port = inter['ovs_port'];
	    		ip_address = inter['ip_address'];
	    		mac_address = inter['mac_address'];

	    		inter_html = 	"<tr>"
	    					+			"<td>" + i_name + "</td>"
	    					+			"<td>" + ovs_port + "</td>"
	    					+			"<td>" + ip_address + "</td>"
	    					+			"<td>" + mac_address + "</td>"
	    					+	"</tr>"	

	    		interfacesList.append(inter_html);
	    	}
		},
		error : function(jqXHR, textStatus, errorThrown) {
        	console.log('ERROR:'+ textStatus + '-' + errorThrown);   
		} 
	 });	
}

function flowTableFormatEmptyFields(field){
	if(typeof field == 'undefined'){
		return '*';
	}
	else{
		return field;
	}
}

function serviceEmptyFields(field){
	if((typeof field == 'undefined') || (field == null)){
		return '*';
	}
	else{
		return field;
	}
}

function loadNodeFlowTable(node){

	$.ajax({
		dataType: "json",
		url: URL_RYU_FLOW_STATS + node,
		type: "GET",
		success: function(resultData) {
			console.log(resultData);

			var tabla = $("#TabFlowsFlowTable");
			var table_row;
			tabla.empty();

			var flows;
			var match;
			var port_in;
			var dl_src;
			var dl_dst;
			var dl_type;
			var label_in;
			var actions;
			var byte_count;
			var hard_timeout;
			var duration_sec;
			var cookie;
			var idle_timeout;
			var packet_count;
			var priority;

		    
		    	flows = resultData[node];
		    	for(j in flows){
		    		data = flows[j];
		    		match = data["match"];
		    		port_in = match["in_port"];
		    		dl_type = match["dl_type"];
		    		label_in = match["mpls_label"];

		    		actions = data["actions"];
					idle_timeout = data["idle_timeout"];
					cookie = data["cookie"];
					packet_count = data["packet_count"];
					hard_timeout = data["hard_timeout"];
					byte_count = data["byte_count"];
					duration_sec = data["duration_nsec"];
					priority = data["priority"];

					table_row = "<tr>"  
			                       + "<th>" + flowTableFormatEmptyFields(port_in) + "</th>"
			                       + "<th>" + flowTableFormatEmptyFields(dl_src)  + "</th>"
			                       + "<th>" + flowTableFormatEmptyFields(dl_dst)  + "</th>"
			                       + "<th>" + flowTableFormatEmptyFields(dl_type) + "</th>"
			                       + "<th>" + flowTableFormatEmptyFields(label_in) + "</th>"

			                       + "<th>" + flowTableFormatEmptyFields(actions) + "</th>"
			                       + "<th>" + flowTableFormatEmptyFields(byte_count) + "</th>"
			                       + "<th>" + flowTableFormatEmptyFields(packet_count) + "</th>"
			                       + "<th>" + flowTableFormatEmptyFields(duration_sec) + "</th>"
			                       + "<th>" + flowTableFormatEmptyFields(idle_timeout) + "</th>"
			                       + "<th>" + flowTableFormatEmptyFields(priority) + "</th>"
			                  + "</tr>";

			  		tabla.append(table_row);
			  	}			 
	    	
		},
		error : function(jqXHR, textStatus, errorThrown) {
        	console.log('ERROR:'+ textStatus + '-' + errorThrown);   
		} 
	 });
}
function loadNodeMPLSTables(node){
	
	var router_id = nodes_data[node].router_id;
	$.ajax({
		dataType: "json",
		url: URI_API_REST_TOPOLOGY_NODE_MPLS_FTN + '/' + router_id,
		type: "GET",
		success: function(resultData) {
			
			var service_name;
			var service_ingress_node;
			var service_egress_node;
			var service_color;
			var service_ingres_int;
			var service_egress_int;
			var mpls_action;
			var label;

			var data;
			var service;
			var nhlfe;
			var nhlfes;
			var next_hop;
			var interfaz;

			var tabla = $("#TabMplsFTNTable");
			var table_row;
			tabla.empty();

		    for(k in resultData){
		    	data = resultData[k];
		    	service = data["service"];
		    	service_name = service["name"];
				service_ingress_node = service["ingress_node"];
			 	service_egress_node = service["egress_node"];
				service_color = service["color"];
				service_ingres_int = service["ingress_interface"];
				service_egress_int = service["egress_interface"];
				nhlfes = data["nhlfes"];

				for(j in nhlfes){
					nhlfe = nhlfes[j];
					next_hop = nhlfe["next_hop"];
					interfaz = nhlfe["intreface"];

					mpls_action = nhlfe["action"]["action"];
					label = nhlfe["action"]["label"];

					table_row = "<tr>"  
			                       + "<th>" + service_name + "</th>"
			                       + "<th>" + service_ingress_node + "</th>"
			                       + "<th>" + service_egress_node + "</th>"

			                       + "<th>" + interfaz + "</th>"
			                       + "<th>" + next_hop + "</th>"
			                       + "<th>" + mpls_action + "</th>"
			                       + "<th>" + label + "</th>"
			                  + "</tr>";

			  		tabla.append(table_row); 
				}
   					 
	    	}
		},
		error : function(jqXHR, textStatus, errorThrown) {
            
        }
	});	

	$.ajax({
		dataType: "json",
		url: URI_API_REST_TOPOLOGY_NODE_MPLS_ILM + '/' + router_id,
		type: "GET",
		success: function(resultData) {
			
			var label_in;
			var mpls_action;

			var data;
			var nhlfe;
			var nhlfes;
			var next_hop;
			var interfaz;

			var tabla = $("#TabMplsILMTable");
			var table_row;
			tabla.empty();

		    for(k in resultData){
	
		    	data = resultData[k];
		    	label_in = data["label"];
				nhlfes = data["nhlfes"];

				for(j in nhlfes){
					nhlfe = nhlfes[j];
					next_hop = nhlfe["next_hop"];
					interfaz = nhlfe["intreface"];

					mpls_action = nhlfe["action"]["action"];
					label = nhlfe["action"]["label"];

					table_row = "<tr>"  
			                       + "<th>" + label_in + "</th>"
			                       + "<th>" + interfaz + "</th>"
			                       + "<th>" + next_hop + "</th>"
			                       + "<th>" + mpls_action + "</th>"
			                       + "<th>" + label + "</th>"
			                  + "</tr>";

			  		tabla.append(table_row); 
				}
   					 
	    	}
		},
		error : function(jqXHR, textStatus, errorThrown) {
            
        }
	});			
}
function updateServicesRender2(new_render_checked){
	/*Oculta todos los servicios anteriormente renderizados*/

	/*Muestra los nuevos*/
	var s;
	var data;
	var color;
	var lsp;
	var link;
	var link_ID;
	var link_color;

	links_colors = {};

	for(i in new_render_checked){
		s = new_render_checked[i];
		data = services_topo_data[s];
		console.log(data);
		color = data.color;

		for(j in data.lsps){
			lsp = data.lsps[j];

			for(k in lsp.links){
				link = lsp.links[k];
				console.log(link);	
				
				link_ID = link.src_datapath_id + '-' + link.src_ovs_port + '-' + link.dst_datapath_id + '-' +  link.dst_ovs_port;
				
				if(link_ID in links_colors){
					links_colors[link_ID].push(color);
				}
				else{
					c = new Array();
					c.push(color);
					links_colors[link_ID] = c;
					
				}

				console.log('LINK-ID' + link_ID);

				$('#'+link_ID).css({stroke: link_color});
			}
			console.log(lsp);
		}
	}


	var colors;
	var stroke_width;
	var linkHTML;
	var x1;
	var x2;
	var y1;
	var y2;

	var caso;
	var x0_1;
	var x0_2;
	var y0_1;
	var y0_2;
	var xi_1;
	var xi_2;
	var yi_1;
	var yi_2;
	var a;
	var b;
	var x_norm;
	var y_norm;
	var alpha;
	var betha;
	var gama;
	var new_stroke_width;

	for(i in links_colors){
		colors = links_colors[i];
		linkHTML = $('#'+i);
		stroke = linkHTML.css('stroke-width');
		n = colors.length;
		s = stroke.substring(0, stroke.length-2);
		new_stroke_width = s/n;

		x1 = linkHTML.attr("x1");
		x2 = linkHTML.attr("x2");
		y1 = linkHTML.attr("y1");
		y2 = linkHTML.attr("y2");

		console.log("s:" + s);
		console.log("x1:" + x1);
		console.log("x2:" + x2);
		console.log("y1:" + y1);
		console.log("y2:" + y2);

		x_norm = Math.abs(x2 - x1);
		y_norm = Math.abs(y2 - y1);
		alpha = Math.atan(x_norm/y_norm);
		betha = 180 - (90 + alpha);
		gama = 360 - (90 + betha);

		console.log('alpaha:' + alpha);
		console.log('betha:' + betha);
		console.log('gamma:' + gama);

		/* Calcula los puntos de referencia X0_1(x0_1, y0_1), X0_2(x0_2, y0_2)*/
		a = Math.cos(betha) * s/(2*n);
		b = Math.sin(betha) * s/(2*n);

		console.log('a:' + a);
		console.log('b:' + b);
		
		if((x1 < x2) && (y1 < y2)){
			/* Caso 4 */
			x0_1 = x1 - a;  
			y0_1 = y1 + b;

			x0_2 = x2 - a;  
			y0_2 = y2 + b;
			caso = 4;
		}
		else if((x1 < x2) && (y1 > y2)){
			/* Caso 3 */
			x0_1 = x1 + a;  
			y0_1 = y1 + b;

			x0_2 = x2 + a;  
			y0_2 = y2 + b;
			caso = 3;
		}
		else if((x1 > x2) && (y1 < y2)){
			/* Caso 6 */
			x0_1 = x1 - a;  
			y0_1 = y1 + b;

			x0_2 = x2 - a;  
			y0_2 = y2 + b;
			caso = 6;
		}
		else if((x1 > x2) && (y1 > y2)){
			/* Caso 5 */
			x0_1 = x1 + a;  
			y0_1 = y1 + b;

			x0_2 = x2 + a;  
			y0_2 = y2 + b;
			caso = 5;
		}

		for(i=1; i<=n ;i++){
			a = Math.cos(betha) * s/(2*i); 
			b = Math.sin(betha) * s/(2*i);

			console.log('a:' + a);
			console.log('b:' + b);
			console.log('x01:' + x0_1);
			console.log('x02:' + x0_2);
			console.log('y01:' + y0_1);
			console.log('y02:' + y0_2);

			switch(caso){
				case 1: ;
					break;
				case 2: ;
					break;
				case 3: x = {x: x0_1 - a, y: y0_1 - b};
						y = {x: x0_2 - a, y: y0_2 - b}; 						
						$("#topology").append("<line stroke-width='" + new_stroke_width + "px' stroke='" + colors[i-1]  
							+ "' class='' id='11-3-13-" + i 
							+ "' x1=" + x.x + " y1=" + x.y + " x2=" + y.x + " y2=" + y.y + "></line>");
					break;
				case 4: x = {x: x0_1 - a, y: y0_1 + b};
						y = {x: x0_2 - a, y: y0_2 + b}; 						
						$("#topology").append("<line stroke-width='" + new_stroke_width + "px' stroke='" + colors[i-1] 
							+ "' class='' id='11-3-13-" + i 
							+ "' x1=" + x.x + " y1=" + x.y + " x2=" + y.x + " y2=" + y.y + "></line>");
					break;	
				case 5: x = {x: x0_1 - a, y: y0_1 - b};
						y = {x: x0_2 - a, y: y0_2 - b}; 						
						$("#topology").append("<line stroke-width='" + new_stroke_width + "px' stroke='" + colors[i-1] 
							+ "' class='' id='11-3-13-" + i  
							+ "' x1=" + x.x + " y1=" + x.y + " x2=" + y.x + " y2=" + y.y + "></line>");
					break;
				case 6: x = {x: x0_1 + a, y: y0_1 - b};
						y = {x: x0_2 + a, y: y0_2 - b}; 						
						$("#topology").append("<line stroke-width='" + new_stroke_width + "px' stroke='" + colors[i-1] 
							+ "' class='' id='11-3-13-" + i 
							+ "' x1=" + x.x + " y1=" + x.y + " x2=" + y.x + " y2=" + y.y + "></line>");
					break;
			}	
		}
	}

	/*Actualiza los servicios renderizados*/
	srvs_render_checked = new_render_checked
}

function updateServicesRender(new_render_checked){
	
	var s;
	var data;
	var color;
	var lsp;
	var link;
	var link_ID;
	var link_color;

	/*Oculta todos los servicios anteriormente renderizados*/
	for(l in links_colors){
		$("#" + l).css("stroke", "");
		$("#" + l).attr("stroke", "#090909");
	}

	srvs_render_checked = [];
	links_colors = {};

	/*Muestra los nuevos*/
	for(i in new_render_checked){

		console.log('tamo aca');

		s = new_render_checked[i];
		data = services_topo_data[s];
		console.log(data);
		color = data.color;

		for(j in data.lsps){
			lsp = data.lsps[j];

			for(k in lsp.links){
				link = lsp.links[k];
				console.log(link);	
				
				link_ID = link.src_datapath_id + '-' + link.src_ovs_port + '-' + link.dst_datapath_id + '-' +  link.dst_ovs_port;
				console.log('LINK-ID' + link_ID);

				if(link_ID in links_colors){
					links_colors[link_ID].push(color);
				}
				else{
					c = new Array();
					c.push(color);
					links_colors[link_ID] = c;
					
				}
				colors = links_colors[link_ID];
				
				link_color = combineColors(colors);
				
				console.log('color: ' + link_color + 'link: ' + link_ID);
				$('#'+link_ID).css({stroke: link_color});
			}
			console.log(lsp);
		}
	}

	/*Actualiza los servicios renderizados*/
	srvs_render_checked = new_render_checked
}

function loadTopologyData(callBackHandller){

	$.ajax({
		dataType: "json",
		url: URI_API_REST_TOPOLOGY,
		type: "GET",
		success: function(resultData) {

			var router_id;
			var datapath_id;
			var status;
			var top_type;
			var of_ready;
			var description;
			var ls_ready;
			var net_type;
			var name;
			var iface;
			var mac_address;
			var ip_address;
			var type;
			var ovs_port;
			var if_name;

			var interfaces = {};
			nodes_data = {};

		    for(k in resultData){
		    	data = resultData[k];
		    	router_id = data["router_id"];
				datapath_id = data["datapath_id"];
			 	status = data["status"];
				top_type = data["top_type"];
				of_ready = data["of_ready"];
				description = data["description"];
				ls_ready = data["ls_ready"];
				net_type = data["net_type"];
				name = data['name'];

				interfaces = {};
				for(i in data['interfaces']){
					iface = data['interfaces'][i];
					ip_address = iface['ip_address'];
					mac_address = iface['mac_address'];
					ovs_port = iface['ovs_port'];
					type = iface['type'];
					if_name = iface['name'];

					interfaces[ip_address] = {'name': if_name, 
												'ip_address': ip_address,
												'mac_address': mac_address,
												'ovs_port': ovs_port,
												'type': type
											}
				}

   				nodes_data[datapath_id] = {'name': name,
   											'router_id': router_id, 
   											'datapath_id': datapath_id,
   											'status': status,
   											'top_type': top_type,
   											'of_ready': of_ready, 
   											'description': description,
   											'ls_ready': ls_ready,
   											'net_type': net_type,
   											'interfaces': interfaces
   										}
		    	 
	    	}

	    	if((typeof callBackHandller != 'undefined') && (callBackHandller != null)){
	    		callBackHandller();
	    	}
	    	else{
	    		loadMiniInfoBoxes();
	    	}
		},
		error : function(jqXHR, textStatus, errorThrown) {
            
        }
	});		
}

function loadServicesTopologyData(){

	$.ajax({
		dataType: "json",
		url: URI_API_REST_SERVICES_LSPS,
		type: "GET",
		success: function(resultData) {
			services_topo_data = {};
			var id;
			var data;

		    for(k in resultData){
		    	data = resultData[k];
		    	id = data["ID"];
				services_topo_data[id] = {"ID": id, "color": data["color"], name: data["name"], "lsps": data["lsps"]};
				
			}
		},
		error : function(jqXHR, textStatus, errorThrown) {
            
        }
	});		
}

function loadMiniInfoBoxes(){
	var node;
	var info_window;
	var infoBoxArrow;
	var node_name;
	for(key in nodes_data){
		node = nodes_data[key];

		node_name = node['name'];
		if((node_name == null) || (node_name == 'undefined')){ node_name = 'switch'}
		info_window = "<div id='miniInfoBoxNode-" + node['datapath_id'] + "' class='miniInfoBox'>"
						
				    +   "<div class='miniInfoBox-wrapper'>"
				    +     "<h4>" + node_name + "</h4>"
				    +     "<hr></hr>"
				    +     "<p>datapath-id: " + node['datapath_id']  + "</p>"
				    +     "<p>router-id: " + node['router_id'] + "</p>"
				    +     "<p>descripcion: " + node['description']+ "</p>"
				    +   "</div>"
				  	+ "</div>"

		$('#miniInfoBoxesNodes').append(info_window);
		
		infoBoxArrow = "<span id='miniInfoBoxNodeArrow-" + node['datapath_id'] + "' class='miniInfoBox-Arrow'></span>";
	  	$('#miniInfoBoxesNodes').append(infoBoxArrow);
	}
	  		
}
function datapathIDToInt(value){
	return parseInt(value, 16);
}

function showMiniInfoBoxNode(dpid, left, top, object_width, object_height){

	if(dpid in nodes_data){
		var data = nodes_data[dpid];
		var infoBox = $('#miniInfoBoxNode-' + dpid);
		var infoBoxArrow = $('#miniInfoBoxNodeArrow-'+dpid);
		var container = $('#tab-1-topo');
		var container_width = container.width();
		var container_height = container.height();
		

		//Get Top and Left coordinates for InfoWindow from left and top event coordinates
		var height = infoBox.height();
		var width = infoBox.width();
		var coords = calculateCoordinatesInfoBox(container_width, container_height, left, top, height, width, object_width, 
												object_height, infoBoxArrow);
		
		infoBox.css({top: coords[0], left: coords[1], position:'absolute'});
		infoBoxArrow.css({top: coords[2], left: coords[3], position:'absolute'});
		//infoBox.toggle();
		//infoBoxArrow.toggle();
		infoBox.show();
		infoBoxArrow.show();
	}
}

function  calculateCoordinatesInfoBox(container_width, container_height, left, top, height, width, object_width, object_height, info_arrow){
	var coords = [];
	var border_margin = 20;
	var object_margin = 12;
	var coords_2 = [];
	var arrow_width = 30;
	var arrow_height = 15;

	if((top - (height + object_margin + border_margin)) >= 0){ 
		coords.push(top - (height + object_margin));
		coords_2.push(top - arrow_height);
		info_arrow.removeClass();
		info_arrow.addClass("miniInfoBox-Arrow bottom");
	}
	else if((top + height + object_margin + border_margin) <= container_height){
		coords.push(top + object_margin + object_height);
		coords_2.push(top + object_height);
		info_arrow.removeClass();
		info_arrow.addClass("miniInfoBox-Arrow top");
	}
	else{
		coords.push(container_height/2);
	}


	if(((left - (width/2 + border_margin)) >= 0) && ((left + (width/2 + border_margin)) <= container_width)){
		coords.push(left - width/2 + object_width/2);
		coords_2.push(left + object_width/2 - arrow_width/2)
	}
	else if(((left + (width/2 + border_margin)) > container_width) && 
		((left - (width - (container_width - left - border_margin))) >= 0)){
		coords.push(container_width - (border_margin + width));
		coords_2.push(left + object_width/2 - arrow_width/2);
	}
	else if((left + (width - (left - border_margin))) <= (container_width - border_margin)) {
		coords.push(border_margin);
		coords_2.push(left + object_width/2 - arrow_width/2);
	}
	else{
		coords.push(container_width /2);
		coords_2.push(left + object_width/2 - arrow_width/2);
	}

	return coords.concat(coords_2);
}
function loadConfigTabData(){
	//By default load Service Tabs data
	loadConfigTabServiceTabData();
}

function loadConfigTabServiceTabData(){
	$.ajax({
		dataType: "json",
		url: URI_API_REST_SERVICES,
		type: "GET",
		success: function(resultData) {
			var tabla1 = $("#TabConfigServicesTable");
			tabla1.empty();
			var tabla2 = $("#TabTopologyServiceRenderSelectorTable");
			tabla2.empty();

			var s;
			var content = "";
		    for(k in resultData){
		    	s = resultData[k];
		    	content = "<tr>"   
			            +    "<td>" + s['service_name'] + "</td>"
			            +    "<td>" + s['ingress_node'] + "</td>"
			            +    "<td>" + s['egress_node'] + "</td>"
			            +    "<td>" + s['ingress_interface'] + "</td>"
			            +    "<td>" + s['egress_interface'] + "</td>"   
			           
				tabla1.append( content + "<td><input class='TabConfigServicesTableSlct'" 
									   + " name='ServiceSlct' value='" + s['ID'] + "' id='' type='radio'></td>" 
			          				   + " </tr>"
			          		);

			    tabla2.append( content + "<td><input class='TabTopologySelectServiceRenderTableSlct'" 
									   + " name='ServiceSlct' value='" + s['ID'] + "' id='' type='checkbox'></td>" 
			          				   + " </tr>"
			          		);

	          	services_data[s['ID']] = s;
				 
	    	}
		},
		error : function(jqXHR, textStatus, errorThrown) {
            
        }
	});	
}

function clearDataModalService(){
	$('#expandService_serviceName').empty();
	$('#expandService_IngressNode').empty();
	$('#expandService_EgressNode').empty();
	$('#expandService_IngressInterface').empty();
	$('#expandService_EgressInterface').empty();
	$('#expandService_etherSrc').empty();
	$('#expandService_etherDst').empty();
	$('#expandService_Ethertype').empty();
	$('#expandService_vlanID').empty();
	$('#expandService_vlanPCP').empty();
	$('#expandService_ipProtocol').empty();
	$('#expandService_ipSrc').empty();
	$('#expandService_ipDst').empty();	
	$('#expandService_ICMPProtocol').empty();
	$('#expandService_icmpCode').empty();
	$('#expandService_icmpType').empty();
	$('#expandService_layer4Protocol').empty();
	$('#expandService_layer4SrcPort').empty();
	$('#expandService_layer4DstPort').empty();	
}

function loadDataModalService(ID){
	clearDataModalService();
	data = services_data[ID];	

	$('#expandService_serviceName').append(serviceEmptyFields(data['service_name']));
	$('#expandService_IngressNode').append(data['ingress_node']);
	$('#expandService_EgressNode').append(data['egress_node']);
	$('#expandService_IngressInterface').append(data['ingress_interface']);
	$('#expandService_EgressInterface').append(data['egress_interface']);

	$('#expandService_etherSrc').append(serviceEmptyFields(data['eth_src']));
	$('#expandService_etherDst').append(serviceEmptyFields(data['eth_dst']));
	$('#expandService_Ethertype').append(serviceEmptyFields(data['eth_type']));
	$('#expandService_vlanID').append(serviceEmptyFields(data['vlan_vID']));
	$('#expandService_vlanPCP').append(serviceEmptyFields(data['vlan_PCP']));

	if((data['IPv4_src'] != null) || (data['IPv4_dst'] != null)){
		$('#expandService_ipProtocol').append('IPv4');
		$('#expandService_ipSrc').append(serviceEmptyFields(data['IPv4_src']));
		$('#expandService_ipDst').append(serviceEmptyFields(data['IPv4_dst']));	
	}
	else if((data['IPv6_src'] != null) || (data['IPv6_dst'] != null)){
		$('#expandService_ipProtocol').append('IPv6');
		$('#expandService_ipSrc').append(serviceEmptyFields(data['IPv6_src']));
		$('#expandService_ipDst').append(serviceEmptyFields(data['IPv6_dst']));	
	}
	else{
		$('#expandService_ipProtocol').append(serviceEmptyFields(null));
		$('#expandService_ipSrc').append(serviceEmptyFields(null));
		$('#expandService_ipDst').append(serviceEmptyFields(null));		
	}

	if((data['ICMPv4_code'] != null) || (data['ICMPv4_type'] != null)){
		$('#expandService_ICMPProtocol').append('ICMPv4');
		$('#expandService_icmpCode').append(serviceEmptyFields(data['ICMPv4_code']));
		$('#expandService_icmpType').append(serviceEmptyFields(data['ICMPv4_type']));
	}
	else if((data['ICMPv6_code'] != null) || (data['ICMPv6_type'] != null)){
		$('#expandService_ICMPProtocol').append('ICMPv6');
		$('#expandService_icmpCode').append(serviceEmptyFields(data['ICMPv6_code']));
		$('#expandService_icmpType').append(serviceEmptyFields(data['ICMPv6_type']));	
	}
	else{
		$('#expandService_ICMPProtocol').append(serviceEmptyFields(null));
		$('#expandService_icmpCode').append(serviceEmptyFields(null));
		$('#expandService_icmpType').append(serviceEmptyFields(null));		
	}

	if((data['TCP_src'] != null) || (data['TCP_dst'] != null)){
		$('#expandService_layer4Protocol').append('TCP');
		$('#expandService_layer4SrcPort').append(serviceEmptyFields(data['TCP_src']));
		$('#expandService_layer4DstPort').append(serviceEmptyFields(data['TCP_dst']));
	}
	else if((data['UDP_src'] != null) || (data['UDP_dst'] != null)){
		$('#expandService_layer4Protocol').append('UDP');
		$('#expandService_layer4SrcPort').append(serviceEmptyFields(data['UDP_src']));
		$('#expandService_layer4DstPort').append(serviceEmptyFields(data['UDP_dst']));	
	}
	else if((data['SCTP_src'] != null) || (data['SCTP_dst'] != null)){
		$('#expandService_layer4Protocol').append('SCTP');
		$('#expandService_layer4SrcPort').append(serviceEmptyFields(serviceEmptyFields(data['SCTP_src'])));
		$('#expandService_layer4DstPort').append(serviceEmptyFields(serviceEmptyFields(data['SCTP_dst'])));	
	}
	else{
		$('#expandService_layer4Protocol').append(serviceEmptyFields(null));
		$('#expandService_layer4SrcPort').append(serviceEmptyFields(null));
		$('#expandService_layer4DstPort').append(serviceEmptyFields(null));		
	}
	

	$('#serviceExpandModal').foundation('reveal', 'open');		
}

function loadDataModalUpdateService(ID){
	clearDataModalService();
	data = services_data[ID];	

	loadDataCombosNodeIngressNodeEgressUpdate("updateServiceForm", data);
	
}



function processServiceForm(type){
	/* type=1 -> Service New type=2 -> service update*/

	var IDs = '';
	var prefix;
	if(type == 1){
		prefix = 'addServiceForm';
	}
	else{
		prefix = 'updateServiceForm';
		IDs = $('#' + prefix + '_serviceID').val(); 
	}

	var service_name = $('#' + prefix + '_serviceName').val(); 
	var ingress_node = $('#' + prefix + '_IngressNode').val();
	var egress_node = $('#' + prefix + '_EgressNode').val();
	var ingress_interface = $('#' + prefix + '_IngressInterface').val();
	var egress_interface = $('#' + prefix + '_EgressInterface').val();
	//var switch_port_in = $('#addServiceForm_switchPortIn').val();
	//var switch_phy_port_in = $('#addServiceForm_physicalSwitchPortIn').val();
	var ether_src = $('#' + prefix + '_etherSrc').val();
	var ether_dst = $('#' + prefix + '_etherDst').val();
	var ether_type = $('#' + prefix + '_Ethertype').val();
	var vlan_vid = $('#' + prefix + '_vlanID').val();
	var vlan_pcp = $('#' + prefix + '_vlanPCP').val();
	var arp_spa = $('#' + prefix + '_ARPspa').val();
	var arp_tpa = $('#' + prefix + '_ARPtpa').val();

	var ip_protocol = $('#' + prefix + '_IPProtocol').val();
	var ipv4_src = '';
	var ipv4_dst = '';
	var ipv6_src = '';
	var ipv6_dst = '';
	var ip_proto = '';
	if((typeof ip_protocol != 'undefined')){
		if(ip_protocol == 0){
			ipv4_src = $('#' + prefix + '_ipSrc').val();
			ipv4_dst = $('#' + prefix + '_ipDst').val();
		}
		else if(ip_protocol == 1){
			ipv6_src = $('#' + prefix + '_ipSrc').val();
			ipv6_dst = $('#' + prefix + '_ipDst').val();
		}
	}	

	var icmp_protocol = $('#' + prefix + '_ICMPProtocol').val();
	var icmpv4_code = '';
	var icmp4_type = '';
	var icmpv6_code = '';
	var icmpv6_type = '';
	if((typeof icmp_protocol != 'undefined')){
		if(icmp_protocol == 0){
			icmpv4_code = $('#' + prefix + '_icmpCode').val();
			icmp4_type = $('#' + prefix + '_icmpType').val();
		}
		else if(icmp_protocol == 1){
			icmpv6_code = $('#' + prefix + '_icmpCode').val();
			icmpv6_type = $('#' + prefix + '_icmpType').val();
		}
	}	

	var layer4_protocol = $('#' + prefix + '_layer4Protocol').val();
	var tcp_src = '';
	var tcp_dst = '';
	var udp_src = '';
	var udp_dst = '';
	var sctp_src = '';
	var sctp_dst = '';
	if((typeof layer4_protocol != 'undefined')){
		if(layer4_protocol == 0){
			tcp_src = $('#' + prefix + '_layerSrcPort').val();
			tcp_dst = $('#' + prefix + '_layerDstPort').val();
			if(((typeof tcp_src != 'undefined') && (tcp_src != '')) || ((typeof tcp_dst != 'undefined') && (tcp_dst != ''))){
				ip_proto = '0x06';
			}
		}
		else if(layer4_protocol == 1){
			udp_src = $('#' + prefix + '_layerSrcPort').val();
			udp_dst = $('#' + prefix + '_layerDstPort').val();
			if(((typeof udp_src != 'undefined') && (udp_src != '')) || ((typeof udp_dst != 'undefined') && (udp_dst != ''))){
				ip_proto = '0x11';	
			}
		}
		else if(layer4_protocol == 2){
			sctp_src = $('#' + prefix + '_layerSrcPort').val();
			sctp_dst = $('#' + prefix + '_layerDstPort').val();
			if(((typeof sctp_src != 'undefined') && (sctp_src != '')) || ((typeof sctp_dst != 'undefined') && (sctp_dst != ''))){
				ip_proto = '0x84';	
			}
		}
	}

	var serviceColor = $('#' + prefix + '_serviceColorPicker').val();
	var serviceColor_rgb = hexToRgb('#' + serviceColor);
	serviceColor = 'RGB(' + serviceColor_rgb.r + ',' + serviceColor_rgb.g + ',' + serviceColor_rgb.b + ')';

	var vpn_type = '';
	if($("#addServiceForm_VPN3").is(':checked')){
		vpn_type = 3;	
	}
	else if($("#addServiceForm_VPN2").is(':checked')){
		vpn_type = 2;	
	};

	data = {'ingress_node': ingress_node, 'egress_node': egress_node, 'ingress_interface': ingress_interface, 
			'egress_interface': egress_interface, 'eth_src': ether_src, 'eth_dst': ether_dst, 'eth_type': ether_type, 
			'vlan_vID': vlan_vid, 'vlanPCP': vlan_pcp, 'ARP_spa': arp_spa, 'ARP_tpa': arp_tpa, 
			'IPv4_src': ipv4_src, 'IPv4_dst': ipv4_dst, 'IPv6_src': ipv6_src,
			'IPv6_dst': ipv6_dst, 'ICMPv4_type': icmp4_type, 'ICMPv4_code': icmpv4_code,'ICMPv6_type': icmpv6_type, 
			'ICMPv6_code': icmpv6_code, 'TCP_src': tcp_src, 'TCP_dst': tcp_dst, 'UDP_src': udp_src, 'UDP_dst': udp_dst,
			'SCTP_src': sctp_src, 'SCTP_dst': sctp_dst, 'service_name': service_name, 'service_color': serviceColor, 
			'ID': IDs, 'IP_proto': ip_proto, 'VPN_service_type': vpn_type
			}
	
	if(validateServiceForm(data)){
		if(type == 1){
			postService(data);
		}
		else{
			putService(data);
		}
	}
}

function postNodeExtraData(data, rid){
	$.ajax({
		dataType: "json",
		data: JSON.stringify(data),
		url: URI_API_REST_TOPOLOGY_NODE + '/' + rid,
		type: "POST",
		success: function(resultData) {
		    $('#configTabNodesSubTabEdit').foundation('reveal', 'close');
		    loadConfigTabNodesSubTabData();
		    selectedNodeConfigTab = null;	
		},
		error : function(jqXHR, textStatus, errorThrown) {

        }
	});
}

function postNodeInterfaceExtraData(data, rid, ip_address){
	$.ajax({
		dataType: "json",
		data: JSON.stringify(data),
		url: URI_API_REST_TOPOLOGY_NODE_INTERFACE + '/' + rid,
		type: "POST",
		success: function(resultData) {
		    $('#configTabInterfaceSubTabEdit').foundation('reveal', 'close');
		    loadConfigTabNodesSubTabData();
		    selectedNodeConfigTab = null;
		    selectedNodeIfaceTab = null;

		    clearEditNodeInterfacesTable();	
		},
		error : function(jqXHR, textStatus, errorThrown) {

        }
	});
}

function postService(data){
	$.ajax({
		dataType: "json",
		data: JSON.stringify(data),
		url: URI_API_REST_SERVICES,
		type: "POST",
		success: function(resultData) {
		    $('#serviceAddModal').foundation('reveal', 'close');
		    loadConfigTabServiceTabData();	
		},
		error : function(jqXHR, textStatus, errorThrown) {

        }
	});
}

function putService(data){
	$.ajax({
		dataType: "json",
		data: JSON.stringify(data),
		url: URI_API_REST_SERVICES,
		type: "PUT",
		success: function(resultData) {
		    $('#serviceUpdateModal').foundation('reveal', 'close');
		    loadConfigTabServiceTabData();	
		},
		error : function(jqXHR, textStatus, errorThrown) {

        }
	});
}

function deleteService(sid){
	$.ajax({
		dataType: "json",
		url: URI_API_REST_SERVICE + '/' + sid,
		type: "DELETE",
		success: function(resultData) {
			console.log('success');
			loadConfigTabServiceTabData();	  
		},
		error : function(jqXHR, textStatus, errorThrown) {
        	console.log('error: ' + textStatus + ' - ' + errorThrown );	     
        }
	});
}

function serviceToJson(){

}

function loadDataCombosNodeIngressNodeEgressUpdate(combo, data){
	$.ajax({
		dataType: "json",
		url: URI_API_REST_TOPOLOGY_DATAPATHS,
		type: "GET",
		success: function(resultData) {
			$("#" + combo + "_IngressNode").empty();
			$("#" + combo + "_IngressNode").append("<option value='-1' text='--Seleccionar--''>--Seleccionar--</option>");
			$("#" + combo + "_EgressNode").empty();
			$("#" + combo + "_EgressNode").append("<option value='-1' text='--Seleccionar--''>--Seleccionar--</option>");

		    for(k in resultData){
			    $("#" + combo + "_IngressNode").append("<option value='" + k + "' text='" + resultData[k] + "''>" + resultData[k] + "</option>");
				$("#" + combo + "_EgressNode").append("<option value='" + k + "' text='" + resultData[k] +"''>" + resultData[k] + "</option>");
	    	}

	    	$('#updateServiceForm_serviceID').val(data['ID']);
			$('#updateServiceForm_serviceName').val(data['service_name']);
			$('#updateServiceForm_IngressNode').val(data['ingress_node']);
			$('#updateServiceForm_EgressNode').val(data['egress_node']);
			loadDataComboNodeIngressInterfaces(data['ingress_node'], "updateServiceForm", data['ingress_interface']);
			loadDataComboNodeEgressInterfaces(data['egress_node'], "updateServiceForm", data['egress_interface']);

			var rgbcolors = parseRGBString(data['service_color']);
			var hexColor = rgbTohex(data['service_color']);

			$('#updateServiceForm_serviceColorPicker').val(hexColor);
			$('#updateServiceForm_serviceColorPicker').css('border-color', '#'+hexColor);

			$('#updateServiceForm_etherSrc').val(data['eth_src']);
			$('#updateServiceForm_etherDst').val(data['eth_dst']);
			$('#updateServiceForm_Ethertype').val(data['eth_type']);
			$('#updateServiceForm_vlanID').val(data['vlan_vID']);
			$('#updateServiceForm_vlanPCP').val(data['vlan_PCP']);


			if((data['IPv4_src'] != null) || (data['IPv4_dst'] != null)){
				$('updateServiceForm_ipProtocol').val(1);
				$('#updateServiceForm_ipSrc').val(data['IPv4_src']);
				$('#updateServiceForm_ipDst').val(data['IPv4_dst']);	
			}
			else if((data['IPv6_src'] != null) || (data['IPv6_dst'] != null)){
				$('#updateServiceForm_ipProtocol').val(2);
				$('#updateServiceForm_ipSrc').val(data['IPv6_src']);
				$('#updateServiceForm_ipDst').val(data['IPv6_dst']);	
			}

			if((data['ICMPv4_code'] != null) || (data['ICMPv4_type'] != null)){
				$('#updateServiceForm_ICMPProtocol').val(1);
				$('#updateServiceForm_icmpCode').val(data['ICMPv4_code']);
				$('#updateServiceForm_icmpType').val(data['ICMPv4_type']);
			}
			else if((data['ICMPv6_code'] != null) || (data['ICMPv6_type'] != null)){
				$('#updateServiceForm_ICMPProtocol').val(2);
				$('#updateServiceForm_icmpCode').val(data['ICMPv6_code']);
				$('#updateServiceForm_icmpType').val(data['ICMPv6_type']);	
			}

			if((data['TCP_src'] != null) || (data['TCP_dst'] != null)){
				$('#updateServiceForm_layer4Protocol').val(3);
				$('#updateServiceForm_layer4SrcPort').val(data['TCP_src']);
				$('#updateServiceForm_layer4DstPort').val(data['TCP_dst']);
			}
			else if((data['UDP_src'] != null) || (data['UDP_dst'] != null)){
				$('#updateServiceForm_layer4Protocol').val(4);
				$('#updateServiceForm_layer4SrcPort').val(data['UDP_src']);
				$('#updateServiceForm_layer4DstPort').val(data['UDP_dst']);	
			}
			else if((data['SCTP_src'] != null) || (data['SCTP_dst'] != null)){
				$('#updateServiceForm_layer4Protocol').val(5);
				$('#updateServiceForm_layer4SrcPort').val(data['SCTP_src']);
				$('#updateServiceForm_layer4DstPort').val(data['SCTP_dst']);	
			}
			

			$('#serviceUpdateModal').foundation('reveal', 'open');		
		},
		error : function(jqXHR, textStatus, errorThrown) {
            
        }
	});
}

function loadDataCombosNodeIngressNodeEgress(combo){
	$.ajax({
		dataType: "json",
		url: URI_API_REST_TOPOLOGY_DATAPATHS,
		type: "GET",
		success: function(resultData) {
			$("#" + combo + "_IngressNode").empty();
			$("#" + combo + "_IngressNode").append("<option value='-1'>--Seleccionar--</option>");
			$("#" + combo + "_EgressNode").empty();
			$("#" + combo + "_EgressNode").append("<option value='-1'>--Seleccionar--</option>");
			 
		    for(k in resultData){
			    $("#" + combo + "_IngressNode").append("<option value=" + k + ">" + resultData[k] + "</option>");
				$("#" + combo + "_EgressNode").append("<option value=" + k + ">" + resultData[k] + "</option>");
	    	}
	    	$("#" + combo + "_IngressNode option").eq(0).prop('selected', true);
	    	$("#" + combo + "_EgressNode option").eq(0).prop('selected', true);

	    	//loadDataComboNodeIngressInterfaces($("#" + combo + "_IngressNode option").val(), combo, null);
	    	//loadDataComboNodeEgressInterfaces($("#" + combo + "_EgressNode option").val(), combo, null);
		},
		error : function(jqXHR, textStatus, errorThrown) {
            
        }
	});
}

function loadDataComboNodeIngressInterfaces(value, combo, combo_value){
	$.ajax({
		dataType: "json",
		url: URI_API_REST_TOPOLOGY_NODE_INTERFACE + '/' + value,
		type: "GET",
		success: function(resultData) {
		    $("#" + combo + "_IngressInterface").empty();
		    for(k in resultData){
			    $("#" + combo + "_IngressInterface").append("<option value=" + resultData[k] + ">" + resultData[k] + "</option>");
	    	}

	    	if(combo_value != null){
	    		$("#" + combo + "_IngressInterface").val(combo_value);	
	    	}
		},
		error : function(jqXHR, textStatus, errorThrown) {
            
        }
	});
}

function loadDataComboNodeEgressInterfaces(value, combo, combo_value){
	$.ajax({
		dataType: "json",
		url: URI_API_REST_TOPOLOGY_NODE_INTERFACE + '/' + value,
		type: "GET",
		success: function(resultData) {
		    $("#" + combo + "_EgressInterface").empty();
		    for(k in resultData){
			    $("#" + combo + "_EgressInterface").append("<option value=" + resultData[k] + ">" + resultData[k] + "</option>");
	    	}

	    	if(combo_value != null){
	    		$("#" + combo + "_EgressInterface").val(combo_value);	
	    	}
		},
		error : function(jqXHR, textStatus, errorThrown) {
            
        }
	});
}

function hexToRgb(hex) {
    // Expand shorthand form (e.g. "03F") to full form (e.g. "0033FF")
    var shorthandRegex = /^#?([a-f\d])([a-f\d])([a-f\d])$/i;
    hex = hex.replace(shorthandRegex, function(m, r, g, b) {
        return r + r + g + g + b + b;
    });

    var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16)
    } : null;
}

function rgbTohex(rgb){
 rgb = rgb.match(/^rgba?[\s+]?\([\s+]?(\d+)[\s+]?,[\s+]?(\d+)[\s+]?,[\s+]?(\d+)[\s+]?/i);
 return (rgb && rgb.length === 4) ? "" +
  ("0" + parseInt(rgb[1],10).toString(16)).slice(-2) +
  ("0" + parseInt(rgb[2],10).toString(16)).slice(-2) +
  ("0" + parseInt(rgb[3],10).toString(16)).slice(-2) : '';
}

function parseRGBString(value){
	var result;
	var aux = value.substring(4, value.length-1).split(",");
	
	result = [aux[0], aux[1], aux[2]];		
	return result;	
}

function combineColors(colors){
	if(colors.length == 0){
		return 'RGB(0,0,0)';
	}
	else if(colors.length == 1){
		return colors[0];
	}
	else{
		var r_sum  = 0;
		var g_sum = 0;
		var b_sum = 0;
		var aux;
		for(var i=0; i<colors.length; i++){
			//RGB(0,0,0)
			aux = colors[i].substring(4, colors[i].length-1).split(",");
			
			r_sum += aux[0];
			g_sum += aux[1];
			b_sum += aux[2];
	
		} 
		var r = Math.round(r_sum / colors.length);
		var g = Math.round(g_sum / colors.length);
		var b = Math.round(b_sum / colors.length);

		return "RGB(" + r + "," + g + "," + b + ")";
	}
}

function combineColors2(colors){
    colors_ini = [];

    for(i in colors){
    	colors_ini.push($.Color(colors[i]));
    }
   
    //Mixing colors
    color = Color_mixer.mix(colors);

    return color;
}


// ************************************************** //
// ******* FORM VALIDATIONS                 ********* //
function validateServiceForm(){

	var errors = false;

	if((data.service_name == 'undefined') || (data.service_name == '')){
		errors = true;
		$("#addServiceForm_serviceName").addClass("error");
		$("#addServiceForm_serviceName_validate").show();
	}
	else{
		$("#addServiceForm_serviceName").removeClass("error");
		$("#addServiceForm_serviceName_validate").hide();
	}

	if((data.ingress_node == 'undefined') || (data.ingress_node == '') || (data.ingress_node == '-1')){
		errors = true;
		$("#addServiceForm_IngressNode").addClass("error");
		$("#addServiceForm_IngressNode_validate").show();
	}
	else{
		$("#addServiceForm_IngressNode").removeClass("error");
		$("#addServiceForm_IngressNode_validate").hide();
	}

	if((data.egress_node == 'undefined') || (data.egress_node == '') || (data.egress_node == '-1')){
		errors = true;
		$("#addServiceForm_EgressNode").addClass("error");
		$("#addServiceForm_EgressNode_validate").show();
	}
	else{
		$("#addServiceForm_EgressNode").removeClass("error");
		$("#addServiceForm_EgressNode_validate").hide();
	}

	if((data.ingress_interface == 'undefined') || (data.ingress_interface == '')){
		errors = true;
	}

	if((data.egress_interface == 'undefined') || (data.egress_interface == '')){
		errors = true;
	}
	
	return !errors;	
}


