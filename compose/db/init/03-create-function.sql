\c rinha_de_backend ;
create or replace function array_to_string_immutable(arr anyarray, sep text, onnull text)
returns text language sql immutable parallel safe strict
as $$
	select array_to_string(arr, sep, onnull);
$$;
