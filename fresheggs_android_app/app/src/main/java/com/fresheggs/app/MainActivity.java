package com.fresheggs.app;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.SharedPreferences;
import android.graphics.Bitmap;
import android.os.Bundle;
import android.text.InputType;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.EditText;
import android.widget.FrameLayout;
import android.widget.ProgressBar;

/** Shows the FreshEggs website inside an app. The server address is asked for once. */
public class MainActivity extends Activity {
    private static final String PREFS = "fresheggs";
    private static final String KEY_URL = "server_url";
    // 10.0.2.2 reaches the computer's localhost from the Android emulator.
    private static final String DEFAULT_URL = "http://10.0.2.2:5000";

    private WebView web;
    private ProgressBar progress;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        FrameLayout root = new FrameLayout(this);
        web = new WebView(this);
        progress = new ProgressBar(this, null, android.R.attr.progressBarStyleHorizontal);
        progress.setIndeterminate(true);
        progress.setVisibility(View.GONE);
        root.addView(web, new FrameLayout.LayoutParams(-1, -1));
        root.addView(progress, new FrameLayout.LayoutParams(-1, 8));
        setContentView(root);

        web.getSettings().setJavaScriptEnabled(true);
        web.getSettings().setDomStorageEnabled(true);
        web.setWebViewClient(new WebViewClient() {
            @Override public void onPageStarted(WebView v, String url, Bitmap icon) { progress.setVisibility(View.VISIBLE); }
            @Override public void onPageFinished(WebView v, String url) { progress.setVisibility(View.GONE); }
            @Override public void onReceivedError(WebView v, WebResourceRequest req, WebResourceError err) {
                if (req.isForMainFrame()) {
                    v.loadData("<h2>Cannot reach the FreshEggs server</h2>"
                        + "<p>Make sure the server is running and the phone is on the same Wi-Fi.</p>"
                        + "<p>Use the menu (top right) &rarr; <b>Server address</b> to change it.</p>",
                        "text/html", "UTF-8");
                }
            }
        });

        String saved = getSharedPreferences(PREFS, MODE_PRIVATE).getString(KEY_URL, null);
        if (saved == null) askForAddress(true); else web.loadUrl(saved);
    }

    private void askForAddress(boolean firstRun) {
        final EditText input = new EditText(this);
        input.setInputType(InputType.TYPE_TEXT_VARIATION_URI);
        input.setText(getSharedPreferences(PREFS, MODE_PRIVATE).getString(KEY_URL, DEFAULT_URL));
        input.setSelectAllOnFocus(true);
        new AlertDialog.Builder(this)
            .setTitle("Server address")
            .setMessage("Example: http://192.168.1.20:5000 (the computer running FreshEggs)")
            .setView(input)
            .setCancelable(!firstRun)
            .setPositiveButton("Connect", (d, w) -> {
                String url = input.getText().toString().trim();
                if (!url.startsWith("http://") && !url.startsWith("https://")) url = "http://" + url;
                getSharedPreferences(PREFS, MODE_PRIVATE).edit().putString(KEY_URL, url).apply();
                web.loadUrl(url);
            })
            .show();
    }

    @Override public boolean onCreateOptionsMenu(Menu menu) {
        menu.add(0, 1, 0, "Server address");
        menu.add(0, 2, 0, "Reload");
        return true;
    }

    @Override public boolean onOptionsItemSelected(MenuItem item) {
        if (item.getItemId() == 1) askForAddress(false);
        else if (item.getItemId() == 2) web.reload();
        return true;
    }

    @Override public void onBackPressed() {
        if (web.canGoBack()) web.goBack(); else super.onBackPressed();
    }
}
