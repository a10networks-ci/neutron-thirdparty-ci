#!/usr/bin/env ruby

PREAMBLE_STR = "\\[8mha\\:";
POSTAMBLE_STR = "\\[0m";

File.open(ARGV[0]).each do |line|
  if line =~ /^(.*)#{PREAMBLE_STR}(.*)#{POSTAMBLE_STR}(.*)$/
    puts "#{$1[0..-2]} #{$3}"
  else
    puts line
  end
end
