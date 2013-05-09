package gov.cdc.stdguide;

import android.os.Bundle;
import android.view.Menu;
import org.apache.cordova.*;
import gov.cdc.stdguide.R;

public class StdTxGuide extends DroidGap {

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        //super.setIntegerProperty("splashscreen", R.drawable.splash);
        super.loadUrl(Config.getStartUrl());
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        getMenuInflater().inflate(R.menu.activity_main, menu);
        return true;
    }
}




