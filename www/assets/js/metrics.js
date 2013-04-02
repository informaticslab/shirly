function trackPageView (section, page)
{
        // console.log("In trackPageView");

		// these first vars change most often depending on version and if debug is true
		var appVersion = "0.5.18.1";
		var debug = false;
		var debugLocal = false;
		var cdcServer = "http://tools.cdc.gov/metrics.aspx?";
		var localServer = "http://192.168.2.18:8989/metrics?";

		// server information 
		var server = debugLocal ? localServer : cdcServer;
        // console.log("server = " + server);
		
		// device info from PhoneGap
        var deviceName = device.name;
		var deviceOsName = device.platform;
		var deviceOsVers = device.version;
		var deviceParams = "c54=" + deviceOsName + "&c55=" + deviceOsVers + "&c56=" + deviceName;
        // console.log("deviceParams = " + deviceParams);
		
		// application info
		var appInfoParams = "c53=" + appVersion;
		
		// page information
		var pageName = "contenttitle=" + section + ":" + page;
        // console.log(pageName);
        
        var sectionInfo = "c59=" + section;
		
		// device online status
		var networkStatus = null;
		var networkState = navigator.connection.type;
        // console.log("networkState = " + networkState);

        // device network state
		if (networkState == Connection.NONE)
			networkStatus = "0";
		else
			networkStatus = "1";
		var deviceOnline = "c57=" + networkStatus;
		
		var commonConstParams = "c8=Mobile App&c51=Standalone&c52=STD Guide&c5=eng&channel=IRDA&c58=Content: Browse";
		var prodConstParams = "reportsuite=cdcsynd";
		var debugConstParams = "reportsuite=devcdc";
		var constParams = (debug ? debugConstParams : prodConstParams) + "&" + commonConstParams;
        // console.log("constParams = " + constParams);

		var metricUrl = server + constParams + "&" + deviceParams + "&" + appInfoParams + "&" + deviceOnline + "&" + sectionInfo + "&" + pageName;
		metricUrl = encodeURI(metricUrl);
        // console.log("metric URL = " + metricUrl);
        
        $.get(metricUrl);

}

function trackFullGuidelinesPageView(page)
{
	var section = "Full Guidelines";
    // console.log("In trackFullGuidelinesPageView");
	trackPageView (section, page);

}

function trackMainMenuPageView()
{

	var section = "Main Menu";
    // console.log("In trackMainMenuPageView");
	trackPageView (section, '1');

}

function trackConditionQuickPickDxTxPageView(dxTxPageId)
{
	var qpSection = "Condition Quick Pick: DxTx";
    // console.log("In trackConditionQuickPickDxTxPageView");
	trackPageView (qpSection, dxTxPageId);

}

function trackConditionQuickPickTreatmentPageView(treatmentPageId)
{
	var qpSection = "Condition Quick Pick: Treatment";
    // console.log("In trackConditionQuickPickTreatmentPageView");
	trackPageView (qpSection, treatmentPageId);

}

function trackAboutUsPageView()
{
	var section = "About Us";
    // console.log("In trackAboutUsPageView");
	trackPageView (section, '1');

}


function trackHistoryPdfPageView()
{
	var section = "Taking a Sexual History PDF";
    // console.log("In trackHistoryPdfPageView");
	trackPageView (section, '1');

}

function trackReferencesPageView(page)
{
	var section = "References";
    // console.log("In trackFullGuidelinesPageView");
	trackPageView (section, page);

}

function trackTermsPageView(page)
{
	var section = "Terms and Abbreviations";
    // console.log("In trackFullGuidelinesPageView");
	trackPageView (section, page);

}


