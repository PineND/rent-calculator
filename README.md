# Rent Calculator

An interactive CLI tool for calculating and allocating shared housing rent among tenants. Helps distribute costs fairly while meeting a target semester income goal.

## Quick Start

```bash
./run.sh
```

This script automatically sets up a Python virtual environment, installs dependencies, and runs the program.

## Manual Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python rent_calculator.py
```

## Features

### Interactive Commands

| Command | Description | Example |
|---------|-------------|---------|
| `<name> <+/-amount>` | Adjust a tenant's rent | `pine +50` |
| `<name> =<amount>` | Set a fixed rent for a tenant | `pine =800` |
| `single/double <+/-amount>` | Adjust all rooms of a type | `double +20` |
| `room <n> <+/-amount>` | Adjust a specific room | `room 1 +100` |
| `target <+/-amount>` | Adjust the semester income target | `target -1000` |
| `view rent` | Display the rent table | |
| `view config` | Display current configuration | |
| `reset` | Clear all session adjustments | |
| `refresh` | Reload config.yaml and reset | |
| `help` | Show available commands | |
| `exit` | Quit the program | |

### Multi-Command Support

Commands can be combined with commas:
```
pine +50, double -20, target +500
```

### Adjustment Types

1. **Tenant Adjustments** (`<name> +/-amount`): Modify a specific person's base rent
2. **Rate Adjustments** (`single/double +/-amount`): Modify all rooms of a type
3. **Room Adjustments** (`room N +/-amount`): Modify a specific room (affects all tenants in that room)
4. **Target Adjustments** (`target +/-amount`): Change the semester income goal
5. **Fixed Rents** (`<name> =amount`): Lock a tenant's rent to a specific amount

### Fixed Rents

When a tenant has a fixed rent:
- Their rent is locked to the specified amount (shown in **bold** with an asterisk)
- Other tenants' suggested rents are adjusted via a multiplier to meet the target
- The multiplier = `(target_monthly - fixed_total) / adjustable_total`

## Configuration

Edit `config.yaml` to set up your house:

```yaml
target_semester_income: 47750    # Total income goal per semester
months_per_semester: 5           # Payment period duration

standard_rates:
  single: 1005                   # Base rate for single rooms
  double: 805                    # Base rate for double rooms

rooms:
  1:
    type: double
  4:
    type: single
  7:
    type: single
    custom_rate: 1105            # Override standard rate for this room

tenants:
  1:
    - Thompson
    - Charles
  4:
    - Eddie
  7:
    - Alex
```

### Room Configuration Options

Simple (uses standard rate):
```yaml
1: double
```

Complex (with custom rate):
```yaml
7:
  type: single
  custom_rate: 1105
```

## Output Columns

| Column | Description |
|--------|-------------|
| Room | Room number |
| Name | Tenant name (asterisk indicates fixed rent) |
| Type | Room type (single/double) |
| Base | Base monthly rent from config |
| Adj | Total adjustments (tenant + rate + room) |
| Monthly | Base + Adjustments |
| Suggested | Optimal rent after multiplier (exact decimal) |
| Sem Delta | `(Suggested - Base) * months` - change from base over semester |
| Semester | Total for the semester (`Suggested * months`) |

## How Calculations Work

### Step 1: Calculate Base Rents
Each tenant's base rent comes from either:
- A custom room rate (if configured)
- The standard rate for their room type

### Step 2: Apply Adjustments
```
monthly = base + tenant_adj + rate_adj + room_adj
```

### Step 3: Calculate Multiplier
To meet the target while respecting fixed rents:
```
fixed_total = sum of all fixed rents
adjustable_total = sum of monthly rents for non-fixed tenants
remaining_target = target_monthly - fixed_total
multiplier = remaining_target / adjustable_total
```

### Step 4: Generate Suggested Rents
- Fixed-rent tenants: use their fixed amount
- Others: `monthly * multiplier` (exact decimal value)

### Step 5: Calculate Totals
- Suggested semester = sum of all suggested rents * months
- Above/below target = suggested semester - target semester

## Important Notes

### Decimal Precision
Suggested rents are shown as exact decimal values for optimal distribution. When the target is achievable, the suggested semester total will match the target exactly.

### Fixed Rent Constraints
When using fixed rents, be aware:
- If fixed rents are **below** normal rates, others' rents increase to compensate
- If fixed rents **exceed** the target, the math becomes invalid (negative multiplier)
- Keep fixed rents reasonable relative to the target

### Semester Delta Interpretation
The "Sem Delta" column shows deviation from the **base** rate, not the adjusted rate. This helps visualize how much each tenant pays above or below the standard rate over a semester.

## Project Structure

```
rent-calculator/
├── rent_calculator.py      # Main entry point and state management
├── config.yaml             # House configuration
├── requirements.txt        # Dependencies (pyyaml, rich)
└── helpers/
    ├── __init__.py
    ├── calculator.py       # Pure calculation logic
    ├── commands.py         # Command parsing
    ├── config.py           # Configuration loading
    └── display.py          # Rich table rendering
```

## Dependencies

- **PyYAML**: Configuration file parsing
- **Rich**: Terminal table formatting and colors
