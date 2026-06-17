# FitFindr — Starter Kit


FitFindr is an AI agent that helps users find secondhand clothing listings and style them with their wardrobe. The user gives a natural language request, such as looking for a vintage graphic tee under a certain price. The agent searches the mock listings dataset, chooses the best matching item, suggests an outfit using the user’s wardrobe, and creates a short fit card caption.

The goal of the project is to show how an agent can use multiple tools in a planned order instead of just giving one direct response. FitFindr uses a planning loop so the output of one tool becomes the input for the next tool.

## What's Included

```
ai201-project2-fitfindr-starter/
├── data/
│   ├── listings.json          # 40 mock secondhand listings
│   └── wardrobe_schema.json   # Wardrobe format + example wardrobe
├── utils/
│   └── data_loader.py         # Helper functions for loading the data
├── planning.md                # Your planning template — fill this out first
└── requirements.txt           # Python dependencies
```

## Setup

```bash
pip install -r requirements.txt
```

Set your Groq API key in a `.env` file (get a free key at [console.groq.com](https://console.groq.com)):
```
GROQ_API_KEY=your_key_here
```

## The Mock Listings Dataset

`data/listings.json` contains 40 mock secondhand listings across categories (tops, bottoms, outerwear, shoes, accessories) and styles (vintage, y2k, grunge, cottagecore, streetwear, and more).

Each listing has: `id`, `title`, `description`, `category`, `style_tags`, `size`, `condition`, `price`, `colors`, `brand`, and `platform`.

Load it with:
```python
from utils.data_loader import load_listings
listings = load_listings()
```

## The Wardrobe Schema

`data/wardrobe_schema.json` defines the format your agent uses to represent a user's existing wardrobe. It includes:

- `schema`: field definitions for a wardrobe item
- `example_wardrobe`: a sample wardrobe with 10 items you can use for testing
- `empty_wardrobe`: a starting template for a new user

Load an example wardrobe with:
```python
from utils.data_loader import get_example_wardrobe
wardrobe = get_example_wardrobe()
```

## Where to Start

1. **Read `planning.md` and fill it out before writing any code.**
2. Verify the data loads correctly by running `python utils/data_loader.py`.
3. Build and test each tool individually before connecting them through your planning loop.

Your implementation files go in this same directory. There's no required file structure for your agent code — organize it however makes sense for your design.

## Tool Inventory

### Tool 1: search_listings

**Purpose:**
`search_listings` searches the secondhand clothing listings dataset and returns items that match the user’s request.

**Inputs:**
- `description` (str): keywords describing the item the user wants, such as “vintage graphic tee”
- `size` (str or None): requested size, such as M, S/M, W30, or US 8
- `max_price` (float or None): the highest price the user wants to pay

**Output:**
This tool returns a list of matching listing dictionaries. Each listing includes fields like title, description, category, style tags, size, condition, price, colors, brand, and platform.

**Failure handling:**
If no listings match, it returns an empty list instead of crashing.

---

### Tool 2: suggest_outfit

**Purpose:**
`suggest_outfit` takes the selected listing and the user’s wardrobe, then suggests how to style the new item.

**Inputs:**
- `new_item` (dict): the selected listing from `search_listings`
- `wardrobe` (dict): the user’s wardrobe, including saved clothing items, categories, colors, style tags, and notes

**Output:**
This tool returns a styling suggestion as a string. It recommends outfit pieces and explains why they work with the selected item.

**Failure handling:**
If the wardrobe is empty, it still returns general styling advice instead of raising an error.

---

### Tool 3: create_fit_card

**Purpose:**
`create_fit_card` creates a short social-media-style caption for the selected item and outfit.

**Inputs:**
- `outfit` (str): the outfit suggestion from `suggest_outfit`
- `new_item` (dict): the selected listing from `search_listings`

**Output:**
This tool returns a short caption that mentions the item, platform, price, and outfit vibe.

**Failure handling:**
If the outfit suggestion is missing or empty, it returns a descriptive error message instead of crashing.

---

## Planning Loop Explanation

The agent starts by receiving the user’s query. It parses the query to find important search details, such as the item description, size, and maximum price.

First, the agent calls `search_listings`. If `search_listings` returns an empty list, the agent stores an error message in the session and stops early. This is important because the agent should not call `suggest_outfit` or `create_fit_card` when there is no selected item.

If search results exist, the agent chooses the first result as the best match and stores it as `selected_item`.

Next, the agent calls `suggest_outfit` using the selected item and the wardrobe. The outfit suggestion is stored in the session as `outfit_suggestion`.

Finally, the agent calls `create_fit_card` using the selected item and outfit suggestion. The fit card caption is stored in the session as `fit_card`.

The final response includes:
1. the top listing found,
2. the outfit suggestion,
3. the fit card caption.

---

## State Management

FitFindr uses a session dictionary to pass information between tools. The session dictionary stores all important information from one user interaction.

The session stores:
- the original user query
- parsed search information
- search results
- the selected item
- the wardrobe
- the outfit suggestion
- the fit card caption
- any error message

The state flow is:

User query → parsed search filters → search results → selected item → outfit suggestion → fit card

This makes sure the tools are connected. The selected item from `search_listings` becomes the input for `suggest_outfit`, and the outfit suggestion becomes the input for `create_fit_card`.

---

## Error Handling

FitFindr handles each major failure mode deliberately.

For `search_listings`, I tested a no-results query such as “designer ballgown size XXS under $5.” The tool returned an empty list. The full agent then returned a helpful error message telling the user to broaden the search by raising the max price, using a broader size, or removing a color/style requirement. The agent stopped early and did not call the next tools.

For `suggest_outfit`, I tested the empty wardrobe case. Instead of crashing, the tool gave general styling advice for the selected item. This allows new users to still get value even if they have not entered wardrobe items yet.

For `create_fit_card`, I tested an empty outfit string. The tool returned a clear message saying it needs an outfit suggestion before creating a fit card. It did not raise a Python exception.

---

## Failure Test Example

One failure test I ran was a no-results search:

**User query:**
“designer ballgown size XXS under $5”

**Expected behavior:**
The agent should not find a listing, should store an error message, and should stop before calling `suggest_outfit` or `create_fit_card`.

**Actual behavior:**
The agent returned a helpful message explaining that no listings matched and suggested changing the search. This confirmed that the planning loop branches correctly instead of always calling all three tools.

---

## AI Usage

I used ChatGPT to help turn my planning document into implementation code. I first wrote the tool specs in `planning.md`, including each tool’s purpose, inputs, outputs, and failure modes.

One specific use of AI was for implementing the three functions in `tools.py`. I gave ChatGPT the tool descriptions for `search_listings`, `suggest_outfit`, and `create_fit_card`. It produced function code that matched the planned inputs and outputs. I reviewed the code before using it to make sure each function handled its failure case.

A second specific use of AI was for implementing the planning loop in `agent.py`. I gave ChatGPT my Planning Loop, State Management, Error Handling, and Architecture sections. It helped create a `run_agent()` function that calls `search_listings` first, stops if there are no results, then calls `suggest_outfit`, and finally calls `create_fit_card`.

I did not accept the AI output blindly. I checked that the generated code followed my spec, stored values in the session dictionary, and did not call all tools unconditionally when search results were empty.

---

## Demo Description

The demo shows one complete successful interaction and one failure case.

For the successful interaction, I search for a vintage graphic tee under $30. The agent searches the listings, selects a matching item, suggests an outfit using the example wardrobe, and creates a fit card caption. This shows all three tools working together.

For the failure case, I search for something unrealistic, such as a designer ballgown size XXS under $5. This triggers the no-results branch. The agent returns an error message and stops early instead of trying to style a missing item.

## Reflection

This project helped me understand how agents use tools, planning loops, and state. The most important part was making sure the agent does not just call every tool every time. The agent has to make a decision after `search_listings`: if no results are found, it stops; if results are found, it continues.

The project also showed why error handling matters. Testing failure cases made the agent stronger because I confirmed that it responds gracefully instead of crashing or producing fake output.
