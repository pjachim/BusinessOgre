# Neat Business Layer
The goal of using BusinessOgre is to create a neat business layer that is useful because it shows as much business logic as possible in one place, and that it is so readable that it can (though that is not necessarily a good idea) be handed to a stakeholder 

To achieve that, this page presents a few thoughts for how to accomplish that.

## File Structure
I recommend having a single file that just contains the information for the business layer. For a very basic data retrieval/filter process the business layer might look like this, where the instantiated classes are imported:
```{python}
import data_retrieval as dr
import filter_actions as fr
import make_nice_spreadsheet as mns

# Here is the final function
build_active_customer_report = dr.query_customer_table >> fr.active_customers >> mns.output
```

In this example, the classes are already instantiated, which reduces the ability to pass arguments in the business file. It might be appropriate to, in specific contexts, instantiate the classes inside the business file to clarify the parameters you are passing to workflow blocks.

```{python}
from data_retrieval import DataRetrieval
from filter_actions import FilterAction
from make_nice_spreadsheet import MakeNiceSpreadsheet

query_customer_table = DataRetrieval(
    name='customer_query',
    table='customer',
    columns=['customer_number', 'customer_status']
)

active_customers = FilterAction(
    name='active_filter',
    filters={'customer_status':'ACTIVE'}
)

output = MakeNiceSpreadsheet(output_file='spreadsheet.xlsx')

# Here is the final function
build_active_customer_report = query_customer_table >> active_customers >> output
```

> ### Note:
> To pass arguments to the workflows as in the example above, you need to overwrite the `.__init__()` method.
> ```{python}
> import business_ogre as ogr
> 
> class DataRetrieval(ogr.WorkflowBlock):
>   def __init__(self, name: str, table: str, columns: list[str]):
>       self.table = table
>       self.columns = columns
>
>       # Initializing the base class, since you are
>       # overwriting the __init__().
>       super().__init__(name)
>
>   def action(self, query: str):
>       ...
> ```