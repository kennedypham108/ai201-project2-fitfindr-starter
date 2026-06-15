# FitFindr — planning.md

> Complete this document before writing any implementation code.
> Your spec and agent diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Your planning.md will be reviewed as part of your submission.
> Update it before starting any stretch features.

---

## Tools

List every tool your agent will use. For each tool, fill in all four fields.
You must have at least 3 tools. The three required tools are listed — add any additional tools below them.

### Tool 1: search_listings

**What it does:**
'search_listing' searches the mock clothing listing datasets and returns listing that match the user's request.
it filters by discription keywords, size, max price, category, style tags, colors, brand, condition, and platform when
those details are provided.

**Input parameters:**

- `description` (str): The main item the user is looking for, such as "vitage graphic tee" or "black platform shoes".
- `size` (str): The requested sze, suzh as "M", "S/M", "W20", or "US 8".
- `max_price` (float): The highest price the user wants to pay.
- `category` (str): Clothing type such as "tops", "bottoms", etc....
- `style_tags` (list[str]): Style words from the requested, such as "wintage", "grunge", etc....
- `colors` (list[str]): Colors the user wants, such as "black", "white", etc....

**What it returns:**
A list of matching listing dictionaries sorted by relevance. Each result contains:
- id
- title
- discription
- category
- style_tags
- size
- condition
- price
- colors
- brand
- platform

**What happens if it fails or returns nothing:**
If no listing match, the agen should stop the flow and tell the user:
I couldn't find a listing that matches the search. Try raising your max price, using a broader size,
or removing one style/color requirment.
The agen should not call sugest_outfit with empty input;

---

### Tool 2: suggest_outfit

**What it does:**
suggest_outfit takes the selected listing and the user's wardrobe, then recommends how to style
the new item with pieces the user alread owns. It looks for wardrobe pieces that match by category, color,
and style tags.

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `new_item` (dict): The listing selected from search_listing. It should include fields like title, category, style_tags, colors, price,
and platform.
- `wardrobe` (dict): The user's wardrobe. It has an utem list, and each item includes id, name, category, colors, style_tags, and optional notes.

**What it returns:**
An outfit suggestion dictionary or string that includes:
- the selected new item
- 2-4 wardrobe pieces to pair with it
- a short explanation of why the pieces work together
- styling advice, such as layering, tucking, rolling sleeves, or shoe choice

**What happens if it fails or returns nothing:**
If the wardrobe is empty, the agent should still give a general styling suggestion, but explain that it could not match the item to saved wardrobe pieces.
Example:
Your wardrobe is empty, so I can't pair this with saved items yet. In general, style this with baggy jeans, chunky sneakers, and a cropped jacket for a
streetwear look.

---

### Tool 3: create_fit_card

**What it does:**
create_fit_card turns the selected item and outfit suggestion into a short social meadia-style caption. It should sound casual and mention the item, price, platform, and styling idea.

**Input parameters:**
- `outfit` (dict or str): The outfit suggestion created by suggest_outfit.
- `new_item` (dict): The selected listing from search_listings.

**What it returns:**
A short fit card caption string.
Example:
thrifted this faded grapic tee off depop for $24 and paired it with baggy jeans + chunky sneakers for an easy grunge streetwear fit

**What happens if it fails or returns nothing:**
If the outfit data or selected item is missing, the agent should not create a caption.
It should return:
I need both a selected item and an outfit suggestion before I can create a fit card.

---

### Additional Tools (if any)

<!-- Copy the block above for any tools beyond the required three -->

---

## Planning Loop

**How does your agent decide which tool to call next?**
The agen starts by reading the User's request and extracting search details: item description, size, max price, category, colors, and style tags.

First, the agent calls search_listings. After search_listing returns, the agent checks whether the result list is empty. If the list is empty, the agent stores an error message
in the session and returns that message to the user immediately. It does not cakk suggest_outfit.

If search_listings returns result, the agent selects the first listing as the best match and stores it in session state as selected_item. Then the agen calls suggest_outfit, passing in selected_item and the user's wardrobe.

After suggesti_outfit returns, the agent checks whether the outfit suggestion exists. If the wardrobe was empty, the agent stull gives a general styling suggestion and stores that in session stat as outfit_suggestion.
If no outfit suggestion can be created at all, the agent returns a message explaining what information is missing.

If an outfit suggestion exists, the agent calls creat_fit_card, passing in the outfit suggestion and selected item. The agent stores the result as fit_card.

The agent is done when it can show the user:
- the best matching listing,
- the outfit suggestion,
- the fit card caption.
---

## State Management

**How does information from one tool get passed to the next?**
The agent stores information during the session so each tool can use the output of the previous too.

Session state should track:
- `user_query`: the original user request
- `search_filters`: extracted filters such as description, size, max price, category, colors, and style tags
- `search_results`: the list returned by `search_listings`
- `selected_item`: the top result chosen from `search_results`
- `wardrobe`: the user’s wardrobe, either from `get_example_wardrobe()` or `get_empty_wardrobe()`
- `outfit_suggestion`: the result returned by `suggest_outfit`
- `fit_card`: the caption returned by `create_fit_card`
- `error_message`: any error message that should stop the flow early

Data flows in this order:

User query → search filters → search results → selected item → outfit suggestion → fit card.

The output of `search_listings` becomes the input for `suggest_outfit`. The output of `suggest_outfit` becomes the input for `create_fit_card`.
---

## Error Handling

For each tool, describe the specific failure mode you're handling and what the agent does in response.

| Tool | Failure mode | Agent response |
|------|-------------|----------------|
| search_listings | No results match the query | Tell the user no listings were found and suggest changing the search by raising max price, broadening size, or removing a color/style requirement. Stop the flow and do not call `suggest_outfit`. |
| suggest_outfit | Wardrobe is empty | Tell the user the wardrobe is empty, then give a general styling suggestion based on the new item’s category, colors, and style tags. |
| create_fit_card | Outfit input is missing or incomplete | Tell the user that a selected item and outfit suggestion are required before creating a fit card. Do not create a fake caption. |

---

## Architecture

The user starts by sendning a clothing request. The planning loop reads the request and pulls out filters like item description, size, max price, category, colors, and sytle tags.

The planning loop first sends those dilters to search_listings. If search_listings finds no results, the agent returns an error message and stops. If results are found, the agent saves the best result
as outfit_suggestion.

Finally, the planning loop sends selected item and outfit_suggestion to create_fit_card. This creates the final fit card caption.

The final response to the user includes:
1. the best matching listing,
2. the outfit suggestion,
3. the fit card caption.

Flow:
User query
↓
Planning Loop
↓
search_listings
↓
If no results: return error and stop
↓
If results exist: save selected_item
↓
suggest_outfit
↓
save outfit_suggestion
↓
create_fit_card
↓
Final response to user

---

## AI Tool Plan


**Milestone 3 — Individual tool implementations:**
I will use ChatGPT or Cluade to help me implement each part of the project after I finish the planning document.

For `search_listings`, I will give the AI my Tool 1 spec and ask it to implement the function using `load_listings()` from `data_loader.py`. I will test it with:
- a vintage graphic tee under $30
- a shoe search
- a search that should return no results

For `suggest_outfit`, I will give the AI my Tool 2 spec and the wardrobe schema. I will ask it to make outfit suggestions by matching category, color, and style tags. I will test it with the example wardrobe and with an empty wardrobe.

For `create_fit_card`, I will give the AI my Tool 3 spec and example captions. I will check that it only creates a caption when both the selected item and outfit suggestion exist.

**Milestone 4 — Planning loop and state management:**
I will give ChatGPT or Claude my Planning Loop, State Management, Error Handling, and Architecture sections. I will ask it to build the full planning loop in this order:

search first → stop if no results → suggest outfit → create fit card

I will verify it by running one full example query and checking that each tool is called in the correct order.
---

## A Complete Interaction (Step by Step)

FitFindr helps a user find a clothing listing based on their request, then suggests how to style that item using the user’s wardrobe, and finally creates a short fit card caption. The `search_listings` tool should be called first when the user asks for an item, using fields like description, size, max price, category, style tags, colors, brand, condition, and platform. If no listing matches, FitFindr should stop and tell the user to try changing the search, instead of calling `suggest_outfit` with empty input.

The `suggest_outfit` tool should be called only after a listing is found. It receives the selected new item and the user’s wardrobe, then recommends pieces from the wardrobe that match the item’s style, colors, and category. If the wardrobe is empty, FitFindr should still give a basic styling suggestion, but explain that it cannot match the item to saved wardrobe pieces.

The `create_fit_card` tool should be called last, after an outfit suggestion exists. It turns the selected item and outfit recommendation into a short social-style caption. If the outfit information is missing or incomplete, FitFindr should not create the card and should explain what information is needed.

Write out what a full user interaction looks like from start to finish — tool call by tool call. Use a specific example query.

**Example user query:** "I'm looking for a vintage graphic tee under $30. I mostly wear baggy jeans and chunky sneakers. What's out there and how would I style it?"

**Step 1:**
The agent reads the user query and extracts the search filters:
- description: vintage graphic tee
- max_price: 30
- category: tops
- style_tags: vintage, graphic tee

The agent calls `search_listings`.

**Step 2:**
If `search_listings` returns results, the agent chooses the first result as `selected_item`.

Example selected item:
"Graphic Tee — 2003 Tour Bootleg Style" for $24 on Depop.

The agent saves this item in session state as `selected_item`.

**Step 3:**
The agent calls `suggest_outfit` using the selected item and the user wardrobe.

Because the tee is vintage, grunge, and streetwear, the agent suggests styling it with baggy jeans, black combat boots or chunky sneakers, and a black denim jacket.

The agent saves this as `outfit_suggestion`.

**Step 4:**
The agent calls `create_fit_card` using the selected item and outfit suggestion.

The tool creates a short caption for the outfit.

**Final output to user:**

I found this listing:

Graphic Tee — 2003 Tour Bootleg Style
Price: $24
Platform: Depop
Condition: good

How to style it:
Pair it with baggy jeans, chunky sneakers or black combat boots, and a black denim jacket. This keeps the outfit in a grunge streetwear style.

Fit card:
thrifted this black vintage graphic tee off depop for $24 — styled it with baggy jeans, chunky sneakers, and a black denim jacket for an easy grunge streetwear fit

**Error path:**

If the user asks for something like "pink leather boots under $10" and no results are found, the agent says:

"I couldn't find a listing that matches that search. Try raising your max price, using a broader size, or removing one style/color requirement."

Then the agent stops and does not call `suggest_outfit` or `create_fit_card`.