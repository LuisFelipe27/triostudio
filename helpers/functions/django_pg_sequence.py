from django.db import connection

def idseq(model_class):
	return '{}_id_seq'.format(model_class._meta.db_table)

def get_next_id(model_class):
	cursor = connection.cursor()
	sequence = idseq(model_class)
	cursor.execute("select nextval('%s')" % sequence)
	row = cursor.fetchone()
	cursor.close()
	return row[0]
	
def reset_sequence(model_class, value=1):
	cursor = connection.cursor()
	sequence = idseq(model_class)
	cursor.execute("ALTER SEQUENCE {} RESTART WITH {};".format(sequence, value))