# -*- encoding: utf-8 -*-

def get_string_value(item, groupby_fields):
	value = ''
	for field in groupby_fields:
		if value:
			value += '<==>%s' % item[ field ]

		else:
			value = item[ field ]

	return value

def string_value_to_dict(value):
	return str(value).split('<==>')

def groupby(datatable, groupby_fields):
	data = []
	uniques = []
	for item in datatable:
		values = get_string_value(item, groupby_fields)
		if not values in uniques:
			uniques.append( values )

	for unique in uniques:
		z = {}
		i = 0
		values = string_value_to_dict(unique)
		for field in groupby_fields:
			z[ field ] = values[ i ]
			i += 1

		z['z_items'] = []
		for item in datatable:
			if unique == get_string_value(item, groupby_fields):
				z['z_items'].append(item)

		data.append(z)

	return data

def _get_iterable(data, field):
	aux = []
	for item in data:
		aux.append( item[field] )

	return aux

def avg(items):
	try:
		return reduce(lambda x, y: x + y, items) / len(items)

	except Exception as e:
		return 'N/A'

def aggregate(data, aggregate_fields, with_groupby = False):
	
	data_aux = {}
	is_percent = False
	for aggregate in aggregate_fields:

		if aggregate in ['count', 'percent']: # el valor percent se utiliza para calcular el porcentaje posteriormente
			for field in aggregate_fields[ aggregate ]:
				key = aggregate + '_' + field
				if with_groupby:
					for row in data:
						row[ key ] = len( row['z_items'] )

				else:
					data_aux[ key ] = len( data )

			if aggregate == 'percent':
				is_percent = True

		elif aggregate == 'max':
			for field in aggregate_fields[ aggregate ]:
				key = aggregate + '_' + field
				if with_groupby:
					for row in data:
						row[ key ] = max( _get_iterable(row['z_items'], field) )

				else:
					data_aux[ key ] = max( _get_iterable(data, field) )

		elif aggregate == 'min':
			for field in aggregate_fields[ aggregate ]:
				key = aggregate + '_' + field
				if with_groupby:
					for row in data:
						row[ key ] = min( _get_iterable(row['z_items'], field) )

				else:
					data_aux[ key ] = min( _get_iterable(data, field) )

		elif aggregate == 'avg':
			for field in aggregate_fields[ aggregate ]:
				key = aggregate + '_' + field
				if with_groupby:
					for row in data:
						row[ key ] = avg( _get_iterable(row['z_items'], field) )

				else:
					data_aux[ key ] = avg( _get_iterable(data, field) )

	if is_percent:
		total_count = 0
		if with_groupby:
			for row in data:
				total_count += len( row['z_items'] )

		else:
			total_count += len( data )

		for aggregate in aggregate_fields:
			if aggregate == 'percent':
				for field in aggregate_fields[ aggregate ]:
					key = aggregate + '_' + field
					if with_groupby:
						for row in data:
							if key in row:
								row[ key ] = str( round( (float(row[ key ]) * 100) / total_count, 2) ) + '%'

					else:
						data_aux[ key ] = str( round( (float(data_aux[ key ]) * 100) / total_count, 2) ) + '%'

	if with_groupby:
		return data

	else:
		return [ data_aux ]
	