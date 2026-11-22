# مصدر تطبيقات za7ef

مصدر متوافق مع AltStore وFeather وBatSign وKSign وESign، يضم تطبيقات المطوّر [za7ef](https://github.com/za7ef).

## طريقة الإضافة

انسخ الرابط الآتي وأضفه في قسم المصادر داخل تطبيق التوقيع:

```
https://raw.githubusercontent.com/za7ef/apps-source/main/source.json
```

## التطبيقات المتوفرة

| التطبيق | المعرّف |
|---|---|
| M | `com.za7ef.mapp` |
| Sowtly | `com.za7ef.sawt` |
| صوت لايت (Sawt Lite) | `com.za7ef.sawt.lite` |
| مشغّلي | `com.mohammed.mushaghili` |
| GTV Emu | `com.za7ef.gtvemu` |

## التحديث التلقائي

يُحدَّث ملف المصدر تلقائيًا كل ثلاث ساعات عبر GitHub Actions، إذ يقرأ آخر إصدارات المستودعات ويستخرج رقم الإصدار ومعرّف الحزمة من ملف IPA مباشرة. ويمكن تشغيل التحديث يدويًا من تبويب Actions.

لإضافة تطبيق جديد، يُضاف إدخاله إلى ملف `apps.json`.
