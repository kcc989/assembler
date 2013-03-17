+readme
+
+Casey Collins
+
+Supported Error Checking: WORD does not support character strings,
+Indexed addressing not supported with Immeadiate or Indirect Addressing,
+Bad symbols not supported, returns error if neither base nor pc relative
+addressing work, returns error if there is an attempt to use BR without a
+BASE directive having been declared, only arguments in range for SVC, SHIFTL,
+and SHIFTR are supported, invalid registers not supported for format 2
+instructions, also checks invalid mnemnoics and duplicate labels.
+
+Added 12/15: RESB and RESW now support hex arguments. RESW, RESB, and all
+hex literals now check for invalid hex characters.
