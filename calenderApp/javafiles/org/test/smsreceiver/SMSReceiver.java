package org.test.smsreceiver;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.os.Bundle;
import android.telephony.SmsMessage;

public class SMSReceiver extends BroadcastReceiver {
    private static MyPythonActivity mActivity;  // Changed from PythonActivity to MyPythonActivity
    private static String mCallback;

    public static void start(MyPythonActivity activity, String callback) {  // Changed parameter type
        mActivity = activity;
        mCallback = callback;
    }

    @Override
    public void onReceive(Context context, Intent intent) {
        if (intent.getAction().equals("android.provider.Telephony.SMS_RECEIVED")) {
            Bundle bundle = intent.getExtras();
            if (bundle != null) {
                Object[] pdus = (Object[]) bundle.get("pdus");
                if (pdus != null) {
                    for (Object pdu : pdus) {
                        SmsMessage smsMessage = SmsMessage.createFromPdu((byte[]) pdu);
                        String sender = smsMessage.getOriginatingAddress();
                        String message = smsMessage.getMessageBody();
                        mActivity.runOnUiThread(new Runnable() {
                            @Override
                            public void run() {
                                mActivity.callPythonMethod(mCallback, sender, message);  // Changed this line
                            }
                        });
                    }
                }
            }
        }
    }
}