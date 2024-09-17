import sqlite3

con = sqlite3.connect('test.db')
cur = con.cursor()

cur.executescript(
    """
        CREATE TABLE IF NOT EXISTS
        CHANNELS(
            guildID INT PRIMARY KEY,
            channelID INT
        );
        
        CREATE TABLE IF NOT EXISTS
        LAST(
            guildID INT PRIMARY KEY,
            userID INT,
            timestamp DATETIME,
            letter STR
        );
        
        CREATE TABLE IF NOT EXISTS
        WORDS_USED(
            word STR,
            guildID INT
        );
        
        CREATE TABLE IF NOT EXISTS
        USER(
            userID INT PRIMARY KEY,
            exps INT,
            levels INT,
            nextLevel INT
        );
        
        CREATE TRIGGER IF NOT EXISTS after_insert_channels
        AFTER INSERT ON CHANNELS
        FOR EACH ROW
        BEGIN
            INSERT INTO LAST(guildID, userID, timestamp, letter) 
            VALUES (NEW.guildID, NULL, NULL, NULL);
        END;
        """
)

cur.execute("SELECT channelID FROM CHANNELS WHERE guildID = ?", (2,))
data = cur.fetchone()
print(data)
con.commit()