package org.test.smsreceiver;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.os.Bundle;
import android.telephony.SmsMessage;
import org.kivy.android.PythonActivity;

public class SMSReceiver extends BroadcastReceiver {
    private static PythonActivity mActivity;
    private static String mCallback;

    public static void start(PythonActivity activity, String callback) {
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
                                mActivity.mPythonService.callMethod(mCallback, sender, message);
                            }
                        });
                    }
                }
            }
        }
    }
}