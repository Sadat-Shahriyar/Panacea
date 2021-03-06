DECLARE
		NEW_PASS VARCHAR2(50);
BEGIN
		FOR CUR IN(SELECT USER_ID FROM PERSON ORDER BY ID)
		LOOP
				NEW_PASS := DBMS_CRYPTO.hash(utl_raw.cast_to_raw(CUR.USER_ID), DBMS_CRYPTO.HASH_MD5);
				UPDATE PERSON SET PASSWORD = NEW_PASS
				WHERE USER_ID = CUR.USER_ID;
 					DBMS_OUTPUT.PUT_LINE(NEW_PASS);
		END LOOP;
END;