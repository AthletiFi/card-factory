import csv
import os
from collections import defaultdict
import uuid
import datetime

def sanitize_path(input_path):
    sanitized = input_path.strip('\'"').replace("\\ ", " ").strip()
    if os.path.exists(sanitized):
        return sanitized
    else:
        raise FileNotFoundError(f"Not a valid file path: {sanitized}. Please try again.")

def group_filenames_by_player(csv_path):
    player_groups = defaultdict(list)
    with open(csv_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Split the name if it contains a hyphen
            names = row['first_name'].split('-')
            if len(names) > 1:
                first_name = names[0]
                last_name = '-'.join(names[1:])
            else:
                first_name = row['first_name']
                last_name = row['last_name']
            
            # Combine first and last name
            full_name = f"{first_name} {last_name}".strip()
            player_groups[full_name].append(row)
    return player_groups

def get_existing_records(csv_path):
    existing_records = {}
    with open(csv_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            existing_records[row['full_name']] = row
    return existing_records

def generate_get_highest_slug_query(collection_name):
    return f"""
    SELECT COALESCE(MAX(CAST(SUBSTRING(dashboard_slug FROM '{collection_name}/([0-9]+)$') AS INTEGER)), 0) as max_slug
    FROM public.player_card_images
    WHERE dashboard_slug LIKE '{collection_name}/%';
    """

def generate_check_and_create_competition_query(competition_name):
    return f"""
    WITH competition_check AS (
        SELECT competition_id
        FROM competitions
        WHERE name = '{competition_name}'
    ), new_competition AS (
        INSERT INTO competitions (competition_id, name)
        SELECT gen_random_uuid(), '{competition_name}'
        WHERE NOT EXISTS (SELECT 1 FROM competition_check)
        RETURNING competition_id
    )
    SELECT COALESCE(
        (SELECT competition_id FROM competition_check),
        (SELECT competition_id FROM new_competition)
    ) AS competition_id
    """

def generate_check_collection_query(collection_name):
    return f"""
    SELECT COUNT(*) as record_count
    FROM public.player_card_images
    WHERE dashboard_slug LIKE '{collection_name}/%';
    """

def generate_check_specific_players_query(collection_name, player_list):
    # Clean up player names: remove hyphens, trim spaces
    cleaned_players = [name.replace('-', ' ').strip() for name in player_list]
    player_names = ", ".join([f"'{name}'" for name in cleaned_players])
    
    return f"""
    SELECT DISTINCT ON (p.player_first_name, p.player_last_name)
        p.player_first_name || ' ' || p.player_last_name AS full_name,
        pci.player_id,
        pci.competition_id,
        pci.dashboard_slug
    FROM
        player_card_images pci
    JOIN
        players_team_info pti ON pci.player_id = pti.player_id
    JOIN
        player_identities p ON pti.player_identity = p.id
    WHERE
        pci.dashboard_slug LIKE '{collection_name}%'
        AND LOWER(TRIM(p.player_first_name || ' ' || p.player_last_name)) IN 
            (SELECT LOWER(TRIM(unnest(ARRAY[{player_names}]))))
    ORDER BY
        p.player_first_name, p.player_last_name, pci.dashboard_slug;
    """

def generate_create_missing_records_query(player_groups, existing_players):
    queries = []
    for player, cards in player_groups.items():
        if player not in existing_players:
            first_name, last_name = player.split(' ', 1)
            jersey_number = cards[0]['jersey_number']
            
            queries.append(f"""
            WITH existing_identity AS (
                SELECT id
                FROM player_identities
                WHERE player_first_name = '{first_name}' AND player_last_name = '{last_name}'
            ),
            new_identity AS (
                INSERT INTO player_identities (player_first_name, player_last_name)
                SELECT '{first_name}', '{last_name}'
                WHERE NOT EXISTS (SELECT 1 FROM existing_identity)
                RETURNING id
            ),
            identity_id AS (
                SELECT id FROM existing_identity
                UNION ALL
                SELECT id FROM new_identity
            ),
            existing_player AS (
                SELECT player_id
                FROM players_team_info
                WHERE player_identity = (SELECT id FROM identity_id)
            ),
            new_player AS (
                INSERT INTO players_team_info (player_identity, player_number)
                SELECT (SELECT id FROM identity_id), '{jersey_number}'
                WHERE NOT EXISTS (SELECT 1 FROM existing_player)
                RETURNING player_id
            ),
            player_id AS (
                SELECT player_id FROM existing_player
                UNION ALL
                SELECT player_id FROM new_player
            )
            SELECT player_id
            FROM player_id;
            """)
    
    return queries

def generate_insert_card_images_query(player_groups, collection_name, team_name, existing_players, next_slug_number):
    queries = []

    for player, cards in player_groups.items():
        if player not in existing_players:
            first_name, last_name = player.split(' ', 1)
            for card in cards:
                card_image_url = f"https://athletifi-s3.s3.us-east-2.amazonaws.com/player-card-images/{collection_name}/{card['webp_filename']}"
                dashboard_slug = f"{collection_name}/{next_slug_number}"

                queries.append(f"""
                WITH team_info AS (
                    SELECT team_id 
                    FROM teams 
                    WHERE team_name = '{team_name}'
                )
                INSERT INTO player_card_images (player_id, competition_id, card_image_url, dashboard_slug)
                SELECT 
                    (SELECT player_id FROM players_team_info pti
                     JOIN player_identities pi ON pti.player_identity = pi.id
                     WHERE pi.player_first_name = '{first_name}' AND pi.player_last_name = '{last_name}' 
                     AND pti.team_id = (SELECT team_id FROM team_info)),
                    @competition_id,
                    '{card_image_url}',
                    '{dashboard_slug}'
                ON CONFLICT (dashboard_slug) DO NOTHING;
                -- Note: Conflicts indicate existing records and require manual investigation
                """)
                next_slug_number += 1


    return queries, next_slug_number

def generate_invite_type(collection_name):
    date_suffix = datetime.datetime.now().strftime("%m%d%y")
    return f"qr_code_invite_{collection_name}-{date_suffix}"

def generate_invitation_query(collection_name, invite_type, players_needing_qr):
    dashboard_slug_pattern = f"%{collection_name}%"
    players_condition = " OR ".join([f"pi.player_first_name || ' ' || pi.player_last_name = '{player}'" for player in players_needing_qr])
    return f"""
INSERT INTO public.invitations (guest_email, card, status, invite_type)
SELECT 
    '-' AS guest_email,
    pci.card_image_id AS card,
    'pending' AS status,
    '{invite_type}' AS invite_type
FROM public.player_card_images pci
JOIN public.players_team_info pti ON pci.player_id = pti.player_id
JOIN public.player_identities pi ON pti.player_identity = pi.id
WHERE pci.dashboard_slug LIKE '{dashboard_slug_pattern}'
AND ({players_condition})
ON CONFLICT DO NOTHING;
"""

def generate_qr_redirect_query(invite_type, players_needing_qr):
    players_condition = " OR ".join([f"pi.player_first_name || ' ' || pi.player_last_name = '{player}'" for player in players_needing_qr])
    return f"""
INSERT INTO public.qr_redirects (invite_id)
SELECT i.invite_id
FROM public.invitations i
JOIN public.player_card_images pci ON i.card = pci.card_image_id
JOIN public.players_team_info pti ON pci.player_id = pti.player_id
JOIN public.player_identities pi ON pti.player_identity = pi.id
WHERE i.invite_type = '{invite_type}'
AND ({players_condition})
ON CONFLICT DO NOTHING;
"""

def generate_view_query(collection_name, highest_slug_number):
    return f"""
    SELECT DISTINCT ON (pci.card_image_url) 
        pci.card_image_url,
        qr.qrcode_id,
        pci.dashboard_slug
    FROM 
        public.player_card_images pci
    LEFT JOIN 
        public.invitations i ON i.card = pci.card_image_id
    LEFT JOIN 
        public.qr_redirects qr ON qr.invite_id = i.invite_id
    WHERE 
        pci.dashboard_slug LIKE '{collection_name}/%'
        AND CAST(SUBSTRING(pci.dashboard_slug FROM '{collection_name}/([0-9]+)$') AS INTEGER) > {highest_slug_number}
    ORDER BY 
        pci.card_image_url,
        qr.qrcode_id NULLS LAST,
        pci.dashboard_slug;
    """



def generate_qr_code_check_query(collection_name, player_list):
    cleaned_players = [name.replace('-', ' ').strip() for name in player_list]
    player_names = ", ".join([f"'{name}'" for name in cleaned_players])
    
    return f"""
    SELECT DISTINCT ON (pi.player_first_name, pi.player_last_name) 
        pi.player_first_name || ' ' || pi.player_last_name AS full_name,
        CASE WHEN qr.qrcode_id IS NOT NULL THEN 'Exists' ELSE 'Missing' END AS qr_code_status
    FROM 
        public.player_card_images pci
    JOIN
        public.players_team_info pti ON pci.player_id = pti.player_id
    JOIN
        public.player_identities pi ON pti.player_identity = pi.id
    LEFT JOIN 
        public.invitations i ON i.card = pci.card_image_id
    LEFT JOIN 
        public.qr_redirects qr ON qr.invite_id = i.invite_id
    WHERE 
        pci.dashboard_slug LIKE '{collection_name}/%'
        AND LOWER(TRIM(pi.player_first_name || ' ' || pi.player_last_name)) IN 
            (SELECT LOWER(TRIM(unnest(ARRAY[{player_names}]))))
    ORDER BY 
        pi.player_first_name, pi.player_last_name, qr.qrcode_id NULLS LAST;
    """

def parse_existing_players_csv(csv_path):
    existing_players = []
    try:
        with open(csv_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if 'full_name' in row:
                    existing_players.append(row['full_name'].strip())
                else:
                    print("Error: CSV file does not contain a 'full_name' column.")
                    return None
    except FileNotFoundError:
        print(f"Error: File {csv_path} not found.")
        return None
    except csv.Error as e:
        print(f"Error reading CSV file: {e}")
        return None
    return existing_players

def parse_qr_status_csv(csv_path):
    players_needing_qr = []
    try:
        with open(csv_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['qr_code_status'].strip().lower() == 'missing':
                    players_needing_qr.append(row['full_name'].strip())
    except FileNotFoundError:
        print(f"Error: File {csv_path} not found.")
        return None
    except csv.Error as e:
        print(f"Error reading CSV file: {e}")
        return None
    return players_needing_qr

def main():
    print_welcome_message()
    collection_name = input("Enter the collection name (e.g., summer-select-24): ")
    competition_name = input("Enter the competition name: ")
    team_name = input("Enter the team name: ")

    parsed_csv_path = input("Enter the path to the parsed card data CSV file: ")
    try:
        parsed_csv_path = sanitize_path(parsed_csv_path)
    except FileNotFoundError as e:
        print(e)
        return

    try:
        player_groups = group_filenames_by_player(parsed_csv_path)
    except (ValueError, KeyError) as e:
        print(f"Error processing CSV file: {e}")
        print("Please ensure your CSV file has the correct column names and try again.")
        return

    # Check if collection exists
    check_collection_query = generate_check_collection_query(collection_name)
    print("\nPlease run the following query in pgAdmin to check if the collection exists:")
    print(check_collection_query)
    print("\nIf the count is greater than 0, that means there are records in this collection, and thus the collection already exists.")
    collection_exists = input("\nIs the count greater than 0? (y/n): ").lower() == 'y'

    highest_slug_number = 0
    if collection_exists:
        get_highest_slug_query = generate_get_highest_slug_query(collection_name)
        print("\nPlease run the following query in pgAdmin to get the highest existing slug number:")
        print(get_highest_slug_query)
        highest_slug_number = int(input("\nEnter the max_slug (if no results, enter 0): "))

    next_slug_number = highest_slug_number + 1

    existing_players = []
    if collection_exists:
        # Check for existing players
        print("\nChecking for existing players in the database...")
        player_list = list(player_groups.keys())
        check_specific_players_query = generate_check_specific_players_query(collection_name, player_list)
        
        print("Please run the following query in pgAdmin to check for existing players:")
        print(check_specific_players_query)
        
        existing_players_found = input("\nWere any existing players returned by the query? (y/n): ").lower() == 'y'
        
        if existing_players_found:
            print("\nHow would you like to provide information about existing players?")
            print("1. Enter a comma-separated list of existing player full names")
            print("2. Provide a CSV file with the query results")
            choice = input("Enter your choice (1 or 2): ").strip()
            
            if choice == '1':
                print("\nPlease provide the list of existing player full names (comma-separated):")
                print("Format: 'FirstName LastName' (e.g., 'John Doe, Jane Smith')")
                existing_players_input = input().strip()
                existing_players = [player.strip() for player in existing_players_input.split(',')] if existing_players_input else []
            elif choice == '2':
                csv_path = input("Enter the path to the CSV file with query results: ").strip()
                existing_players = parse_existing_players_csv(sanitize_path(csv_path))
                if existing_players is None:
                    print("Failed to parse the CSV file. Exiting.")
                    return
            else:
                print("Invalid choice. Exiting.")
                return
            
            print(f"Found {len(existing_players)} existing players. Will only create records for new players.")
        else:
            print("No existing players found. Proceeding with creating records for all players.")

    # Generate update queries
    check_and_create_competition_query = generate_check_and_create_competition_query(competition_name)
    create_missing_records_queries = generate_create_missing_records_query(player_groups, existing_players)
    insert_card_images_queries, final_slug_number = generate_insert_card_images_query(
        player_groups, collection_name, team_name, existing_players, next_slug_number
    )

    # Write update queries to a file
    output_file = f"{collection_name}_update_player_info_queries.sql"
    with open(output_file, 'w') as f:
        f.write("BEGIN;\n\n")
        f.write("-- Check if competition exists and create if it doesn't\n")
        f.write("DO $$\n")
        f.write("DECLARE\n")
        f.write("    comp_id UUID;\n")
        f.write("BEGIN\n")
        f.write(f"    {check_and_create_competition_query}\n")
        f.write("    INTO comp_id;\n")
        f.write("    PERFORM set_config('athletifi.competition_id', comp_id::text, false);\n")
        f.write("END $$;\n\n")
        f.write("-- Create missing player records\n")
        for query in create_missing_records_queries:
            f.write(query + "\n")
        f.write("-- Insert or update player card images\n")
        for query in insert_card_images_queries:
            modified_query = query.replace("@competition_id", "(SELECT current_setting('athletifi.competition_id')::uuid)")
            f.write(modified_query + "\n")
        f.write("\nCOMMIT;")

    print(f"\nStep 1: SQL queries for creating/updating records have been written to {output_file}")
    print("Please review and execute this file in pgAdmin.")

    # Get the list of players being added
    players_to_add = list(player_groups.keys())

    # Generate QR code check query
    qr_code_check_query = generate_qr_code_check_query(collection_name, players_to_add)
    print("\nStep 2: Run the following query in pgAdmin to check for existing QR codes for the players being added:")
    print(qr_code_check_query)
    print("\nThis query will return 'Exists' for players with QR codes and 'Missing' for those without.")
    print("You need to create invitations and QR redirect records for players with 'Missing' status.")
    
    create_invitations = input("\nStep 3: Do you need to create invitations and QR redirect records for any players? (y/n): ").lower() == 'y'

    if create_invitations:
        print("\nHow would you like to provide the list of players needing QR codes?")
        print("1. Enter names manually")
        print("2. Upload a CSV file with the query results")
        choice = input("Enter your choice (1 or 2): ").strip()

        if choice == '1':
            print("\nPlease enter the full names of players needing QR codes.")
            print("Format: 'FirstName LastName' (e.g., 'John Doe, Jane Smith')")
            players_input = input("Enter names (comma-separated): ").strip()
            players_needing_qr = [player.strip() for player in players_input.split(',')]
        elif choice == '2':
            csv_path = input("Enter the path to the CSV file with query results: ").strip()
            players_needing_qr = parse_qr_status_csv(sanitize_path(csv_path))
            if players_needing_qr is None:
                print("Failed to parse the CSV file. Exiting.")
                return
        else:
            print("Invalid choice. Exiting.")
            return

        print(f"\nCreating invitations and QR redirects for the following players:")
        for player in players_needing_qr:
            print(f"- {player}")
        
        invite_type = generate_invite_type(collection_name)
        invitation_query = generate_invitation_query(collection_name, invite_type, players_needing_qr)
        qr_redirect_query = generate_qr_redirect_query(invite_type, players_needing_qr)
        
        output_file = f"{collection_name}_invitations_and_qr_redirects.sql"
        
        with open(output_file, 'w') as f:
            f.write("BEGIN;\n\n")
            f.write("-- Generate invitation entries\n")
            f.write(invitation_query)
            f.write("\n-- Generate QR redirect entries\n")
            f.write(qr_redirect_query)
            f.write("\nCOMMIT;\n")
        
        print(f"\nStep 4: SQL queries for invitations and QR redirects have been written to {output_file}")
        print("Please review and execute this file in pgAdmin.")
        print(f"Invite type used: {invite_type}")

    # Generate view query
    view_query = generate_view_query(collection_name, highest_slug_number)
    print("\nStep 5: After executing the above queries, run this query to check QR codes for newly added players and export the results as a CSV file:")
    print(view_query)
    print("\nThis query will return the card_image_url, qrcode_id, and dashboard_slug for each newly added card in the collection.")
    print("Export these results as a CSV file for use in the QR code generation process.")

    print_concluding_message()

def print_welcome_message():
    welcome_text = """
    ╔════════════════════════════════════════════════════════════════════════════╗
    ║            Welcome to AthletiFi Player Card DB Query Generator!            ║
    ╚════════════════════════════════════════════════════════════════════════════╝

    This script helps you update the AthletiFi database with player and player card data
    as part of the player card generation process. It generates SQL queries to check and 
    to add player information into the database, and generate invitations and QR code
    redirect records if needed. 

    ┌──────────────────────────────────────────┐
    │           Before You Begin:              │
    └──────────────────────────────────────────┘
    1. Ensure you have access to the AthletiFi database.
    2. Prepare a CSV file with the following fields: 
    ✦ first_name, last_name, jersey_number, and webp_filename
    *Note: you can use the parse_filenames.py script to generate this automatically.*
    3. Know the collection name, competition name, and team name.

    ┌──────────────────────────────────────────┐
    │                 Important:               │
    └──────────────────────────────────────────┘
    This script generates SQL queries for you to run in pgAdmin. It does not
    directly modify the database. *Always review the generated SQL before execution.*

    Let's get started with updating your AthletiFi player card database!
    """
    print(welcome_text)

def print_concluding_message():
    concluding_message = """
┌──────────────────────────────────────────┐
│               Important Note:            │
└──────────────────────────────────────────┘
The results from this query provide a list of unique card image URLs
along with their associated QR code IDs and dashboard slugs for the newly added
cards in the collection. This ensures each new card image URL appears only once,
prioritizing non-NULL QR code IDs if a card has multiple associated QR codes.

Why this matters:
This CSV file will be crucial for the next step in the process -
generating QR codes for each newly added player card. The unique pairing of card images
and QR code IDs ensures that each new card gets the correct, unique QR code.

What's next:
You'll use this CSV file with the QR code generator script to create
the individual QR codes for each newly added player card. This maintains the link
between the physical card, its digital record, and the QR code that
bridges the two.

Proceed to the QR code generation step with this CSV file to continue the process.
    """
    print(concluding_message)

if __name__ == "__main__":
    main()
