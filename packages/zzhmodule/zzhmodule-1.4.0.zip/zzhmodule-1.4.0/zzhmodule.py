"""This is a module which provides a function called print_list().This
function is can print the list."""
import sys
def print_list (alist , indent = False,level=0,fh=sys.stdout):
	"""�������������������alist��һ�������python�б�
	indent����ȷ���Ƿ���������ܣ�level��ʾ�������ٸ��Ʊ��"""
	for each_item in alist :
		if isinstance( each_item,list):
			print_list(each_item,indent,level+1,fh)
		else :
			if indent :
				for tab_stop in range(level):
					print >> fh,"\t",
			print >> fh,each_item
