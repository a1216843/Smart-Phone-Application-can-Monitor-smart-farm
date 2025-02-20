package com.example.spam_project;

import android.util.Log;

import com.google.android.gms.tasks.OnCompleteListener;
import com.google.android.gms.tasks.Task;
import com.google.firebase.firestore.DocumentReference;
import com.google.firebase.firestore.DocumentSnapshot;
import com.google.firebase.firestore.FirebaseFirestore;

import org.jetbrains.annotations.NotNull;

import java.util.HashMap;
import java.util.Map;

import androidx.annotation.NonNull;

public class Login_Controller {
    public static FirebaseFirestore db = FirebaseFirestore.getInstance();

    public static void User_Check(String User_Email) {
        DocumentReference doc = db.collection("User_info").document(User_Email);
        doc.get().addOnCompleteListener(new OnCompleteListener<DocumentSnapshot>() {
                    @Override
                    public void onComplete(@NonNull @NotNull Task<DocumentSnapshot> task) {
                        if (task.isSuccessful()) {
                            DocumentSnapshot document = task.getResult();
                            if (document.exists()) {
                                Log.d("DB_Check", "User_info 존재함");
                            } else {
                                //등록된 이메일 정보가 아닌 경우 회원 이메일 추가
                                Sign_up(User_Email);
                                Login_Controller.User_Check(User_Email);
                            }
                        } else {
                            Log.d("DB_Check", "읽어오기 실패");
                        }
                    }
                });
    }

    private static void Sign_up(String User_Email) {
        Map<String, Object> data = new HashMap<>();
        data.put("Device_Number", null);
        db.collection("User_info").document(User_Email).set(data);
        Log.d("DB_Check", "User_info 추가");
    }

}
