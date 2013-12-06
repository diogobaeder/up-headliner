local articles = cjson.decode(ARGV[1])
local num_added = 0

for i, article in ipairs(articles) do
    local label = article["collection"] .. "." .. article["category"]
    local set_key = "set." .. label
    local sorted_set_key = "sorted." .. label
    local counts_key = "counts." .. article["collection"]
    if redis.call("SISMEMBER", set_key, article["member"]["url"]) == 0 then
        redis.call("ZADD", sorted_set_key, article["score"], cjson.encode(article["member"]))
        redis.call("SADD", set_key, article["member"]["url"])
        if redis.call("HEXISTS", counts_key, article["category"]) == 0 then
            redis.call("HSET", counts_key, article["category"], 1)
        else
            redis.call("HINCRBYFLOAT", counts_key, article["category"], 1)
        end
        num_added = num_added + 1
    end
end

return num_added
