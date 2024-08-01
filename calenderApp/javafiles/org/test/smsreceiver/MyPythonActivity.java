package org.test.smsreceiver;  // Use your actual package name

import org.kivy.android.PythonActivity;

public class MyPythonActivity extends PythonActivity {
    public void callPythonMethod(String methodName, String arg1, String arg2) {
        mPythonService.callMethod(methodName, arg1, arg2);
    }
}