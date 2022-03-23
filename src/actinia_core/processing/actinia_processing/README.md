The modules in `actinia_processing` are sorted after inheritance.
Because all classes inherit from `ephemeral_processing`, it is on top level.
The modules inside the folder `ephemeral` all inherit directly from this class,
including `persistent_processing`, `ephemeral_processing_with_export` and `renderer_base`
from which the other classes in respective folders inherit.
