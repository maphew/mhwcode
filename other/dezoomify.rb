#!/usr/bin/env ruby
# Dezoomify. See README.markdown.
# By Henrik Nyh <http://henrik.nyh.se> 2009-02-06 under the MIT License.

require 'open-uri'
require 'rubygems'
require 'nokogiri'


ARGV.each_with_index do |page_url, page_url_index|
  puts "#{page_url_index}. Visiting #{page_url}"

  page = Nokogiri::HTML(open(page_url))
  #mhw: paths = page.search('param[name="FlashVars"]').map {|var| var[:value][/zoomifyImagePath=([^"'&]+)/, 1] }
  #     note - openzoom uses lower case 'flashvars' and 'source=' instead of 'zoomifyImagePath='
  paths ="Sheep-Goat-Panorama_img/ImageProperties.xml"

  paths.each_with_index do |path, path_index|
    #mhw: full_path = URI.join(page_url, path+'/')
    full_path = "/mnt/hgfs/X/Share/Sheep-Goat-Panorama_img/"
    puts "  #{page_url_index}.#{path_index} Found image path #{full_path}"


    # <IMAGE_PROPERTIES WIDTH="1737" HEIGHT="2404" NUMTILES="99" NUMIMAGES="1" VERSION="1.8" TILESIZE="256"/>
    #mhw: xml_url = URI.join(full_path.to_s, 'ImageProperties.xml')
    xml_url = '/mnt/hgfs/X/Share/Sheep-Goat-Panorama_img/ImageProperties.xml'
    doc = Nokogiri::XML(open(xml_url))
    props = doc.at('IMAGE_PROPERTIES')

    width = props[:WIDTH].to_i
    height = props[:HEIGHT].to_i
    tilesize = props[:TILESIZE].to_f

    tiles_wide = (width/tilesize).ceil
    tiles_high = (height/tilesize).ceil

    # Determine max zoom level.
    # Also determine tile_counts per zoom level, used to determine tile group.
    # With thanks to http://trac.openlayers.org/attachment/ticket/1285/zoomify.patch.
    zoom = 0
    w = width
    h = height
    tile_counts = []
    while w > tilesize || h > tilesize
      zoom += 1

      t_wide = (w / tilesize).ceil
      t_high = (h / tilesize).ceil
      tile_counts.unshift t_wide*t_high

      w = (w / 2.0).floor
      h = (h / 2.0).floor
    end
    tile_counts.unshift 1  # Zoom level 0 has a single tile.
    tile_count_before_level = tile_counts[0..-2].inject(0) {|sum, num| sum + num }

    files_by_row = []
    tiles_high.times do |y|
      row = []
      tiles_wide.times do |x|
        filename = '%s-%s-%s.jpg' % [zoom, x, y]
        local_filepath = "/tmp/zoomify-#{filename}"
        row << local_filepath

        tile_group = ((x + y * tiles_wide + tile_count_before_level) / tilesize).floor
        #mhw: tile_url = URI.join(full_path.to_s, "TileGroup#{tile_group}/#{filename}")
        tile_url = full_path.to_s, "TileGroup#{tile_group}/#{filename}"
        #mhw: url = URI.join(tile_url.to_s, filename)
        url = tile_url.to_s
        puts "    Getting #{url}..."
        #mhw: 
        url = File.open(url, 'rb')
        File.open(local_filepath, 'wb') {|f| f.print url.read }
      end
      files_by_row << row
    end


    # `montage` is ImageMagick.
    # We first stitch together the tiles of each row, then stitch all rows.
    # Stitching the full image all at once can get extremely inefficient for large images.

    puts "    Stitching #{tiles_wide} x #{tiles_high} = #{tiles_wide*tiles_high} tiles..."

    row_files = []
    files_by_row.each_with_index do |row, index|
      filename = "/tmp/zoomify-row-#{index}.jpg"
      `montage #{row.join(' ')} -geometry +0+0 -tile #{tiles_wide}x1 #{filename}`
      row_files << filename
    end

    filename = "/tmp/zoomified-#{page_url_index}.#{path_index}.jpg"
    `montage #{row_files.join(' ')} -geometry +0+0 -tile 1x#{tiles_high} #{filename}`

    puts "    Done: #{filename}"

    # Reveal in Finder if on OS X.
    `which osascript && osascript -e 'tell app "Finder"' -e 'reveal POSIX file "#{filename}"' -e 'activate' -e 'end'`

  end

end
