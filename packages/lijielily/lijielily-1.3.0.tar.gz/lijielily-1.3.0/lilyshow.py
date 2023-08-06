def showlist(the_list,indent=False,level=0):
     for each_item in the_list:
          if isinstance(each_item,list):
               showlist(each_item,indent,level+1)
          else:
               if indent:
                         print('\t'*level,end='')
               print(each_item)
