# Examples

This directory contains example scripts demonstrating various features of the Radar Target Analyzer.

## Available Examples

### 1. basic_usage.py
Demonstrates the basic workflow:
- Generate synthetic test data
- Extract features
- Tag behavior
- Generate reports

**Run it:**
```bash
python examples/basic_usage.py
```

### 2. batch_processing.py
Shows how to process multiple targets in batch:
- Generate multiple test targets
- Process them all
- Generate summary statistics

**Run it:**
```bash
python examples/batch_processing.py
```

## Creating Your Own Examples

You can create your own examples by following this template:

```python
#!/usr/bin/env python3
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_path))

from radar_analyzer import (
    RadarDataLoader,
    FeatureExtractor,
    TaggingEngine,
    SyntheticDataGenerator
)

# Your code here
```

## Example Outputs

All examples are self-contained and don't require external data files. They generate synthetic data internally for demonstration purposes.

### Expected Runtime
- basic_usage.py: ~2 seconds
- batch_processing.py: ~5 seconds

## Next Steps

After running these examples, try:
1. Modifying the configuration parameters
2. Generating different behavior types
3. Adjusting thresholds for tagging
4. Processing your own radar data files

See the main README.md for more information on using the system with real data.
