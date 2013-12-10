local articles = cjson.decode(ARGV[1])
local category_max = tonumber(ARGV[2])
local num_added = 0
local num_deleted = 0
local cleanup_threshold = 25

for i, article in ipairs(articles) do
    local label = article["collection"] .. "." .. article["category"]
    local set_key = "set." .. label
    local sorted_set_key = "sorted." .. label
    local counts_key = "counts." .. article["collection"]

    -- Using both a set and a sorted set here. Only the sorted set would've been necessary.
    -- However, I'm not sure if content can change while a URL remains the same.
    -- A sorted set alone will not catch that possibility, hence introducing duplicate URL's
    -- with slightly different data.
    if redis.call("SISMEMBER", set_key, article["member"]["url"]) == 0 then
        redis.log(redis.LOG_DEBUG, "adding_article url:" .. article["member"]["url"] .. " label:" .. label)
        redis.call("ZADD", sorted_set_key, article["score"], cjson.encode(article["member"]))
        redis.call("SADD", set_key, article["member"]["url"])
        if redis.call("HEXISTS", counts_key, article["category"]) == 0 then
            redis.call("HSET", counts_key, article["category"], 1)
        else
            redis.call("HINCRBYFLOAT", counts_key, article["category"], 1)
        end
        num_added = num_added + 1
    end

    -- cleanup if category over limit and the threshold for cleanup has been crossed
    local sorted_set_length = redis.call("ZCARD", sorted_set_key)
    if sorted_set_length > (category_max+cleanup_threshold) then
        redis.log(redis.LOG_DEBUG, "cleanup_started for label:" .. label)
        local members = redis.call("ZREVRANGEBYSCORE", sorted_set_key, "+inf", "-inf", "LIMIT", category_max, sorted_set_length)
        for i, member_data in ipairs(members) do
            local member = cjson.decode(member_data)
            redis.log(redis.LOG_DEBUG, "deleting url:" .. member["url"] .. " label:" .. label)
            local category_count = redis.call("HGET", counts_key, article["category"])
            redis.call("SREM", set_key, member["url"])
            redis.call("HSET", counts_key, article["category"], category_count-1)
            redis.call("ZREM", sorted_set_key, member_data)
            num_deleted = num_deleted + 1
        end
    end
end

return {num_added, num_deleted}
