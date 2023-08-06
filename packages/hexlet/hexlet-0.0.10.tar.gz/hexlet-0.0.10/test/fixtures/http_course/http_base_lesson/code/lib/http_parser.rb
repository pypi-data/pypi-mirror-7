require "json"

module HttpParser
  STATES = [:query, :header, :body]

  def self.main
    current_state = :query
    result = {}
    body_parts = []

    while line = gets
      case current_state
      when :query
        result.merge! parse_query(line)
      when :header
        if line != "\r\n"
          result.merge! parse_header(line.strip)
        end
      when :body
        body_parts << line
      end

      if current_state == :query
        current_state = :header
      else
        if line == "\r\n"
          current_state = :body
        end
      end
    end

    result[:body] = body_parts.join("")

    puts JSON.generate(result)
  rescue ArgumentError
    puts JSON.generate({error: "invalid data"})
  end

  def self.parse_header(line)
    matches = line.scan(/(.+?): (.+)/)
    raise ArgumentError if matches.empty?

    values = matches.first
    {values[0] => values[1]}
  end

  def self.parse_query(line)
    matches = line.scan(/(GET|POST|HEAD)\s(\S+?)\sHTTP\/(1\.\d)/)
    raise ArgumentError if matches.empty?

    values = matches.first
    {method: values[0], url: values[1], http_version: values[2]}
  end
end
